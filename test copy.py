import subprocess
import sys
import threading


def run_ollama_stream_chars(image_path):
    """
    Runs the ollama command and yields output characters as they are produced.

    Args:
        image_path (str): The path to the image to be described.

    Yields:
        str: Characters of output from the ollama process.
    """
    command = ["ollama", "run", "llama3.2-vision"]
    input_text = f"describe {image_path}\n"

    # Initialize the subprocess
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,  # Line-buffered
        universal_newlines=True,  # Text mode
    )

    # Function to send input to the subprocess
    def send_input():
        if process.stdin:
            process.stdin.write(input_text)
            process.stdin.flush()
            process.stdin.close()

    # Start a thread to send input to avoid blocking
    input_thread = threading.Thread(target=send_input)
    input_thread.start()

    try:
        # Read stdout character by character
        while True:
            char = process.stdout.read(1)  # Read one character
            if not char:
                break
            yield char

        # Read stderr if there are errors
        stderr_output = process.stderr.read()
        if stderr_output:
            yield f"\nError: {stderr_output}\n"
    except Exception as e:
        yield f"\nError while reading output: {e}\n"
    finally:
        process.stdout.close()
        process.stderr.close()
        process.wait()


# Usage Example
if __name__ == "__main__":
    image_path = "/Users/charan/VSCode/GITHUB/HAR/test2.jpg"

    print(
        "Starting to stream ollama output character by character...\n",
        end="",
        flush=True,
    )
    for output_char in run_ollama_stream_chars(image_path):
        print(output_char, end="", flush=True)
    print("\nStreaming completed.")
