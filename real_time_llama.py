# import ollama

# response = ollama.chat(
#     model="llama3.2-vision",
#     messages=[
#         {
#             "role": "user",
#             "content": "whats in the image?",
#             "images": ["/Users/charan/VSCode/GITHUB/HAR/test2.jpg"],
#         }
#     ],
# )

# print(response)

# import subprocess

# def run_ollama(image_path):
#     command = ["ollama", "run", "llama3.2-vision"]
#     input_text = f"describe {image_path}\n"
#     process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout, stderr = process.communicate(input=input_text.encode())
#     if stderr:
#         print(f"Error: {stderr.decode()}")
#     return stdout.decode()

# image_path = "/Users/charan/VSCode/GITHUB/HAR/test2.jpg"
# response = run_ollama(image_path)
# print(response)


# import subprocess

# def stream_ollama_output(image_path):
#     command = ["ollama", "run", "llama3.2-vision"]
#     input_text = f"describe {image_path}\n"

#     # Use subprocess.Popen to handle streaming
#     process = subprocess.Popen(
#         command,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True  # Ensure text mode for easier streaming
#     )

#     # Send the input and stream the output
#     process.stdin.write(input_text)
#     process.stdin.close()

#     # Stream stdout line by line
#     for line in process.stdout:
#         yield line.strip()  # Stream each line of the output
#     process.stdout.close()

#     # Handle any errors
#     stderr = process.stderr.read()
#     if stderr:
#         yield f"Error: {stderr.strip()}"
#     process.stderr.close()

# # Test the streaming function
# image_path = "/Users/charan/VSCode/GITHUB/HAR/test2.jpg"
# for output in stream_ollama_output(image_path):
#     print(output)

# import subprocess
# import sys
# import threading

# def run_ollama_stream_chars(image_path):
#     """
#     Runs the ollama command and yields output characters as they are produced.

#     Args:
#         image_path (str): The path to the image to be described.

#     Yields:
#         str: Characters of output from the ollama process.
#     """
#     command = ["ollama", "run", "llama3.2-vision"]
#     input_text = f"describe {image_path}\n"

#     # Initialize the subprocess
#     process = subprocess.Popen(
#         command,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         bufsize=1,               # Line-buffered
#         universal_newlines=True, # Text mode
#     )

#     # Function to send input to the subprocess
#     def send_input():
#         if process.stdin:
#             process.stdin.write(input_text)
#             process.stdin.flush()
#             process.stdin.close()

#     # Start a thread to send input to avoid blocking
#     input_thread = threading.Thread(target=send_input)
#     input_thread.start()

#     # Read stdout character by character
#     try:
#         while True:
#             char = process.stdout.read(1)  # Read one character
#             if not char:
#                 break
#             yield char
#     except Exception as e:
#         yield f"Error while reading output: {e}\n"
#     finally:
#         process.stdout.close()
#         process.stderr.close()
#         process.wait()

#         # Optionally, handle any remaining stderr output
#         stderr_output = process.stderr.read()
#         if stderr_output:
#             yield f"Error: {stderr_output}"

# # Usage Example
# if __name__ == "__main__":
#     image_path = "/Users/charan/VSCode/GITHUB/HAR/test2.jpg"

#     print("Starting to stream ollama output character by character...\n", end='', flush=True)
#     for output_char in run_ollama_stream_chars(image_path):
#         print(output_char, end='', flush=True)
#     print("\nStreaming completed.")

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
