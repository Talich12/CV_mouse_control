import cv2
import mediapipe as mp
import math
import pyautogui
import threading

class HandDetector():
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        screen_width, screen_height = pyautogui.size()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x_pixel = 0
        self.y_pixel = 0
        self.click = False

    def calculate_hand_size(self, hand_coords):
        if hand_coords:
            # Находим координаты ладони и большого пальца
            wrist_coord = [coord for coord in hand_coords if coord[0] == 'WRIST'][0][1:]
            thumb_tip_coord = [coord for coord in hand_coords if coord[0] == 'THUMB_TIP'][0][1:]

            # Вычисляем расстояние между ладонью и большим пальцем
            distance = self.find_distance(wrist_coord, thumb_tip_coord)
            # Возвращаем расстояние в пикселях
            return distance
        return 0

    def find_hands(self, img, draw=True):
        results = self.hands.process(img)
        self.left_hand_coords = []
        self.right_hand_coords = []
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if results.multi_handedness[idx].classification[0].label == 'Right':
                    # Сохранение координат точек правой руки вместе с их названиями
                    self.left_hand_coords.extend([(self.mp_hands.HandLandmark(i).name, res.x, res.y, res.z) for i, res in enumerate(hand_landmarks.landmark)])
                elif results.multi_handedness[idx].classification[0].label == 'Left':
                    # Сохранение координат точек левой руки вместе с их названиями
                    self.right_hand_coords.extend([(self.mp_hands.HandLandmark(i).name, res.x, res.y, res.z) for i, res in enumerate(hand_landmarks.landmark)])
        self.find_gesture(self.left_hand_coords, self.right_hand_coords)
        return results

    def find_distance(self, p1, p2):
        d = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        return d

    def draw_landmarks(self, img, results):
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_gesture(self, left_hand_coords, right_hand_coords):
        if len(right_hand_coords) > 0:
            right_size = self.calculate_hand_size(right_hand_coords)
            right__trashhold = right_size * 0.25

            right_thumb_tip = [coord for coord in right_hand_coords if coord[0] == 'THUMB_TIP'][0][1:]
            right_index_finger_tip = [coord for coord in right_hand_coords if coord[0] == 'INDEX_FINGER_TIP'][0][1:]

            right_distance = self.find_distance(right_thumb_tip, right_index_finger_tip)
            if right_distance <= right__trashhold:
                x = right_index_finger_tip[0]
                y = right_index_finger_tip[1]
                x = 1 - x
                self.x_pixel = x * self.screen_width
                self.y_pixel = y * self.screen_height
                #print(f'управление мышкой')
                #print((right_thumb_tip, rightindex_finger_tip))
                #print(self.find_midpoint(right_thumb_tip, rightindex_finger_tip))

        if len(left_hand_coords) > 0:
            left_size = self.calculate_hand_size(left_hand_coords)
            left__trashhold = left_size * 0.25

            left_thumb_tip = [coord for coord in left_hand_coords if coord[0] == 'THUMB_TIP'][0][1:]
            leftindex_finger_tip = [coord for coord in left_hand_coords if coord[0] == 'INDEX_FINGER_TIP'][0][1:]

            left_distance = self.find_distance(left_thumb_tip, leftindex_finger_tip)
            if left_distance <= left__trashhold:
                self.click = True
            else:
                self.click = False
            
def process_frame(hand_detector, cap):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Преобразование изображения в RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Рисование результатов на изображении
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        results = hand_detector.find_hands(image)
        image = hand_detector.draw_landmarks(image, results)

        # Отображение изображения
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

def mouse_movement(hand_detector):
    while True:
        pyautogui.moveTo(hand_detector.x_pixel, hand_detector.y_pixel)


def mouse_click(hand_detector):
    while True:
        if hand_detector.click:
            pyautogui.mouseDown()
            #print('click')
        else:
            pyautogui.mouseUp()
            #print('unclick')


# Захват видео с камеры
cap = cv2.VideoCapture(0)
hand_detector = HandDetector()
pyautogui.FAILSAFE = False
lock = threading.Lock()
frame_thread = threading.Thread(target=process_frame, args=(hand_detector, cap,))
mouse_move_thread = threading.Thread(target=mouse_movement, args=(hand_detector,))
mouse_click_thread = threading.Thread(target=mouse_click, args=(hand_detector,))

frame_thread.start()
mouse_move_thread.start()
mouse_click_thread.start()

frame_thread.join()
mouse_move_thread.join()
mouse_click_thread.join()

cap.release()
cv2.destroyAllWindows()