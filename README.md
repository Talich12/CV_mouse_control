# CV Mouse Control
This project leverages the power of MediaPipe and PyAutoGUI to enable real-time hand gesture recognition and control of a computer's mouse cursor. By using a webcam, the application can detect hand gestures in real-time and translate them into mouse movements, providing an innovative way to interact with digital interfaces.

## Features

- **Real-time Hand Gesture Recognition**: Utilizes MediaPipe's Hands model to detect and recognize hand gestures in real-time.
- **Mouse Control**: Translates detected hand gestures into mouse movements using PyAutoGUI, allowing for precise control of the cursor.
- **Multi-threading**: Separates the video processing and mouse control into different threads, ensuring smooth operation.
- **Customizable Gestures**: The application can be easily extended to recognize and respond to additional hand gestures.