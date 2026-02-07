import cv2
import mediapipe as mp
import math
import numpy as np

# Setup
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

gesture_to_write = "NONE"

# Draw gamepad in bottom-left corner
def draw_gamepad(image, gesture, finger_pos=None):
    h, w, _ = image.shape
    overlay = image.copy()

    # D-pad center position
    center_x, center_y = 100, h - 100
    spacing = 40
    radius = 25

    # Button layout: (position), gesture name, label
    directions = {
        "UP": ((center_x, center_y - spacing), "JUMP", "U"),
        "DOWN": ((center_x, center_y + spacing), "SLIDE", "D"),
        "LEFT": ((center_x - spacing, center_y), "LEFT", "L"),
        "RIGHT": ((center_x + spacing, center_y), "RIGHT", "R"),
    }

    selected_gesture = "NONE"

    for label, (pos, name, symbol) in directions.items():
        px, py = pos
        color = (200, 200, 200)

        # Finger pointing detection
        if finger_pos:
            fx, fy = finger_pos
            if math.hypot(fx - px, fy - py) < 30:
                color = (0, 255, 0)
                selected_gesture = name

        # Draw button
        cv2.circle(overlay, (px, py), radius, color, -1)
        cv2.putText(overlay, symbol, (px - 10, py + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    # Blend overlay for transparency
    cv2.addWeighted(overlay, 0.4, image, 0.6, 0, image)
    return selected_gesture

# Main loop
while True:
    success, image = cap.read()
    image = cv2.flip(image, 1)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_pos = None
    virtual_gesture = "NONE"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            h, w, _ = image.shape

            # Index finger tip
            fx, fy = int(lm[8].x * w), int(lm[8].y * h)
            finger_pos = (fx, fy)

            # Draw landmarks + finger pointer
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(image, (fx, fy), 8, (0, 255, 255), -1)

    # Draw and detect gesture
    virtual_gesture = draw_gamepad(image, gesture_to_write, finger_pos)

    # Write gesture
    if virtual_gesture != "NONE":
        gesture_to_write = virtual_gesture
        with open("gesture.txt", "w") as f:
            f.write(gesture_to_write)

    # Show gesture text
    cv2.putText(image, f"Gesture: {gesture_to_write}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show window
    cv2.imshow("Virtual Gamepad Control", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
