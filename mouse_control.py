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
            right_thumb_tip = [coord for coord in right_hand_coords if coord[0] == 'THUMB_TIP'][0][1:]
            right_index_finger_tip = [coord for coord in right_hand_coords if coord[0] == 'INDEX_FINGER_TIP'][0][1:]
            right_distance = self.find_distance(right_thumb_tip, right_index_finger_tip)
            #print(f'{right_distance} дистанция')
            if right_distance <= 0.045:
                x = right_index_finger_tip[0]
                y = right_index_finger_tip[1]
                x = 1 - x
                self.x_pixel = x * self.screen_width
                self.y_pixel = y * self.screen_height
                print(f'управление мышкой')
                #print((right_thumb_tip, rightindex_finger_tip))
                #print(self.find_midpoint(right_thumb_tip, rightindex_finger_tip))
        if len(left_hand_coords) > 0:
            left_thumb_tip = [coord for coord in left_hand_coords if coord[0] == 'THUMB_TIP'][0][1:]
            leftindex_finger_tip = [coord for coord in left_hand_coords if coord[0] == 'INDEX_FINGER_TIP'][0][1:]
            left_distance = self.find_distance(left_thumb_tip, leftindex_finger_tip)
            if left_distance <= 0.045:
                print('click')
                #pyautogui.click()
            
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
        #image = hand_detector.draw_landmarks(image, results)

        # Отображение изображения
        #cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

def mouse_control(hand_detector):
    while True:
        print(hand_detector.x_pixel)
        pyautogui.moveTo(hand_detector.x_pixel, hand_detector.y_pixel)
    

# Захват видео с камеры
cap = cv2.VideoCapture(0)
hand_detector = HandDetector()
pyautogui.FAILSAFE = False

frame_thread = threading.Thread(target=process_frame, args=(hand_detector, cap,))
mouse_thread = threading.Thread(target=mouse_control, args=(hand_detector,))

frame_thread.start()
mouse_thread.start()

frame_thread.join()
mouse_thread.join()

cap.release()
cv2.destroyAllWindows()