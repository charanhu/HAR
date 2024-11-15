import cv2
import time
import ollama

# Function to capture an image from the webcam
def capture_image(output_path, delay=10):
    cap = cv2.VideoCapture(0)  # Open the default camera (ID 0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return None

    print(f"Starting camera... Please wait {delay} seconds.")
    time.sleep(delay)  # Wait for the specified delay (10 seconds)

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)  # Save the captured image
        print(f"Image captured and saved to {output_path}")
    else:
        print("Error: Unable to capture an image.")
    
    cap.release()  # Release the camera

# Path to save the captured image
image_path = "/Users/charan/VSCode/GITHUB/HAR/captured_image.jpg"

# Capture image after 10 seconds
capture_image(image_path, delay=10)

# Pass the captured image to the Ollama API
response = ollama.chat(
    model="llama3.2-vision",
    messages=[
        {
            "role": "user",
            "content": "What's in the image?",
            "images": [image_path],
        }
    ],
    stream=True,
)

# Print the response from the model
for r in response:
    print(r["message"]["content"])
