import cv2
import mediapipe as mp
import numpy as np
import openai
import pyttsx3
import time
from dotenv import load_dotenv

_ = load_dotenv()
from openai import OpenAI

# Initialize OpenAI API (Replace with your API key)
client = OpenAI()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Initialize MediaPipe Drawing for visualization
mp_drawing = mp.solutions.drawing_utils

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)  # Adjust speech rate if necessary


# Define action classification function
def classify_action(keypoints):
    """
    Simple action classification based on keypoint positions.
    Extend this function with more sophisticated logic or ML models.
    """
    right_wrist = keypoints[16]
    right_shoulder = keypoints[12]

    action = "Standing"

    if right_wrist and right_shoulder:
        wrist_y = right_wrist[1]
        shoulder_y = right_shoulder[1]
        if wrist_y < shoulder_y - 0.1:  # Threshold for raising hand
            action = "Raising Right Hand"

    return action


# Function to get feedback from LLM
def get_llm_feedback(action, history):
    """
    Generate feedback using OpenAI's GPT model based on the current action and history.
    """
    prompt = (
        f"User is currently: {action}.\n"
        f"Provide encouraging and corrective feedback for the user to help them improve their workout."
    )

    print("prompt: ", prompt)

    chat_completion = client.chat.completions.create(
        model="mistral-nemo", messages=[{"role": "user", "content": prompt}]
    )

    feedback = chat_completion.choices[0].message.content
    print("Feedback: ", feedback)
    return feedback


# Function to speak the feedback
def speak_feedback(feedback):
    tts_engine.say(feedback)
    tts_engine.runAndWait()


def main():
    cap = cv2.VideoCapture(0)  # 0 for default webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    action_history = []
    last_feedback_time = 0
    feedback_interval = 5  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and detect poses
        results = pose.process(image)

        # Convert back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        action = "No Action Detected"

        if results.pose_landmarks:
            # Draw pose landmarks on the image
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

            # Extract keypoints
            keypoints = []
            for lm in results.pose_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z, lm.visibility])

            # Classify action based on keypoints
            action = classify_action(keypoints)
            action_history.append(action)

        # Display the action on the image
        cv2.putText(
            image,
            f"Action: {action}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # Periodically get feedback from LLM
        current_time = time.time()
        if current_time - last_feedback_time > feedback_interval:
            if action != "No Action Detected":
                feedback = get_llm_feedback(action, action_history)
                speak_feedback(feedback)
                last_feedback_time = current_time

        # Show the image
        cv2.imshow("Real-Time Fitness Coaching", image)

        # Exit on pressing 'q'
        if cv2.waitKey(5) & 0xFF == ord("q"):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
