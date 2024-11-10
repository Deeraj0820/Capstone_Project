import cv2
from gpiozero import Motor
from time import sleep
import pyttsx3
import numpy as np
import smtplib

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize Hand Detector (replace 'HandDetector' with the correct import path)
from own_hand_detector import HandDetector
detector = HandDetector(maxHands=1, detectionCon=0.8)
video = cv2.VideoCapture(0)

# Initialize Motors
motor_left = Motor(forward=4, backward=3)
motor_right = Motor(forward=23, backward=24)
speed = 0.225
prev_state = "idle"
state = "idle"

while True:
    ret, img = video.read()
    if not ret:
        break

    hand = detector.findHands(img, draw=False)
    if hand:
        lmlist = hand[0]

        if lmlist['type'] == 'Right':
            coords = lmlist['lmList']
            finger_up = detector.fingersUp(lmlist)

            # Draw circles on detected fingertips
            for i in range(1, 6):
                if finger_up[i - 1] == 1:
                    img = cv2.circle(img, (coords[i * 4][0], coords[i * 4][1]), 6, (250, 160, 90), -2)

            # Define actions based on finger configurations
            if finger_up == [0, 1, 0, 0, 0]:  # Left
                print("Left")
                motor_left.forward(speed)
                motor_right.backward(speed)

            elif finger_up == [0, 1, 1, 0, 0]:  # Right
                print("Right")
                motor_left.backward(speed)
                motor_right.forward(speed)

            elif finger_up == [0, 1, 1, 1, 0]:  # Back
                print("Back")
                motor_left.backward(speed)
                motor_right.backward(speed)

            elif finger_up == [0, 1, 1, 1, 1]:  # Forward
                print("Forward")
                motor_left.forward(speed)
                motor_right.forward(speed)

            elif finger_up == [1, 1, 1, 1, 1]:  # Stop
                print("Break")
                motor_left.stop()
                motor_right.stop()

        elif lmlist['type'] == 'Left':
            coords = lmlist['lmList']
            finger_up = detector.fingersUp(lmlist)

            # Draw circles on detected fingertips
            for i in range(1, 6):
                if finger_up[i - 1] == 1:
                    img = cv2.circle(img, (coords[i * 4][0], coords[i * 4][1]), 6, (250, 160, 90), -2)

            # Specific gestures for toilet or washroom
            if finger_up == [0, 0, 0, 0, 1]:
                # engine.say("Toilet")
                # engine.runAndWait()
                state = "toilet"

            elif finger_up == [0, 1, 1, 0, 0]:
                # engine.say("Washroom")
                # engine.runAndWait()
                state = "washroom"

            elif finger_up == [0, 1, 1, 1, 0]:
                print("3")

            elif finger_up == [0, 1, 1, 1, 1]:
                print("4")

            # Send email on state change
            if state != prev_state:
                sender_email = "youremail@gmail.com"
                receiver_email = "receiver@gmail.com"
                password = "yourpassword"
                message = f"To: {receiver_email}\r\nSubject: Gesture\r\n\r\n{state}"

                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
                    print(f"Email has been sent to {receiver_email}")
                except Exception as e:
                    print("Failed to send email:", e)
                finally:
                    server.quit()

                prev_state = state

    cv2.imshow("Video", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
video.release()
cv2.destroyAllWindows()
motor_left.stop()
motor_right.stop()