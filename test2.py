import ollama
import cv2
import os
import tempfile
import time
from threading import Thread, Event, Lock
from queue import Queue

# Configuration
MODEL_NAME = "llama3.2-vision"
FRAME_INTERVAL = 15  # Analyze every 2 seconds
VIDEO_SOURCE = 0  # 0 for webcam, or provide video file path
MAX_ANALYSIS_THREADS = 2  # Limit the number of concurrent analysis threads

# Thread-safe Queue to handle frames for analysis
frame_queue = Queue()
print_lock = Lock()

def analyze_frame(image_path):
    """
    Sends the image at image_path to Ollama for analysis.
    Returns the assistant's response content.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": "What's in the image?",
                    "images": [image_path],
                }
            ],
        )
        # Extract and return the assistant's message
        return response.get('message', {}).get('content', 'No response')
    except Exception as e:
        return f"Error analyzing the image: {e}"

def worker(stop_event):
    """
    Worker thread that processes frames from the queue.
    """
    while not stop_event.is_set():
        try:
            image_path = frame_queue.get(timeout=1)
        except:
            continue  # Continue if queue is empty

        analysis = analyze_frame(image_path)
        with print_lock:
            print(f"Analysis for {os.path.basename(image_path)}: {analysis}")

        # Remove the temporary image file
        try:
            os.remove(image_path)
        except OSError as e:
            with print_lock:
                print(f"Error deleting temp file {image_path}: {e}")

        frame_queue.task_done()

def video_capture(stop_event, last_analyze_time, cap, frame_lock):
    """
    Captures video frames and enqueues them for analysis at specified intervals.
    """
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            with print_lock:
                print("Error: Unable to read from video source.")
            stop_event.set()
            break

        current_time = time.time()
        with frame_lock:
            if current_time - last_analyze_time[0] >= FRAME_INTERVAL:
                last_analyze_time[0] = current_time

                # Save the current frame to a temporary file
                try:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                        temp_image_path = tmp_file.name
                        cv2.imwrite(temp_image_path, frame)
                        frame_queue.put(temp_image_path)
                except Exception as e:
                    with print_lock:
                        print(f"Error saving frame for analysis: {e}")

        # Display the video frame
        cv2.imshow('Real-Time Video Analysis', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    stop_event = Event()
    frame_lock = Lock()
    last_analyze_time = [0]  # Using list for mutable reference

    # Initialize video capture
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print("Error: Unable to open video source.")
        return

    # Start worker threads
    workers = []
    for _ in range(MAX_ANALYSIS_THREADS):
        t = Thread(target=worker, args=(stop_event,))
        t.start()
        workers.append(t)

    try:
        # Start video capture in the main thread
        video_capture(stop_event, last_analyze_time, cap, frame_lock)
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting...")
        stop_event.set()
    finally:
        # Wait for all frames to be processed
        frame_queue.join()
        # Ensure all worker threads are terminated
        for t in workers:
            t.join()

if __name__ == "__main__":
    main()
