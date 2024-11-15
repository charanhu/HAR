# import subprocess
# import sys
# import threading
# from typing import Generator


# def run_ollama_stream_chars(image_path: str) -> Generator[str, None, None]:
#     """
#     Executes the `ollama` command to describe actions in an image and yields output characters in real-time.

#     Args:
#         image_path (str): The path to the image to be described.

#     Yields:
#         str: Individual characters from the `ollama` process output.
#     """
#     command = ["ollama", "run", "llama3.2-vision"]
#     input_text = f"In 30 words describe the human actions in the image {image_path}\n"

#     try:
#         # Initialize the subprocess with context manager for better resource handling
#         with subprocess.Popen(
#             command,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             bufsize=1,  # Line-buffered
#             text=True,  # Use text mode
#         ) as process:

#             # Function to send input to the subprocess
#             def send_input():
#                 try:
#                     if process.stdin:
#                         process.stdin.write(input_text)
#                         process.stdin.flush()
#                         process.stdin.close()
#                 except Exception as e:
#                     # If writing to stdin fails, print the error
#                     print(f"Error sending input to subprocess: {e}", file=sys.stderr)

#             # Start a thread to send input to avoid blocking the main thread
#             input_thread = threading.Thread(target=send_input, daemon=True)
#             input_thread.start()

#             # Read stdout character by character
#             while True:
#                 char = process.stdout.read(1)
#                 if not char:
#                     break
#                 yield char

#             # Wait for the input thread to finish
#             input_thread.join()

#             # Check for errors
#             stderr_output = process.stderr.read()
#             if stderr_output:
#                 yield f"\nError: {stderr_output}\n"

#     except FileNotFoundError:
#         yield "\nError: The 'ollama' command was not found. Please ensure it is installed and in your PATH.\n"
#     except Exception as e:
#         yield f"\nUnexpected error: {e}\n"


# def main(image_path: str):
#     """
#     Main function to stream the output from the `ollama` command.

#     Args:
#         image_path (str): The path to the image to be described.
#     """
#     print(
#         "Starting to stream ollama output character by character...\n",
#         end="",
#         flush=True,
#     )
#     for output_char in run_ollama_stream_chars(image_path):
#         print(output_char, end="", flush=True)
#     print("\nStreaming completed.")


# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print(f"Usage: python {sys.argv[0]} <image_path>")
#         sys.exit(1)

#     image_path_input = sys.argv[1]
#     main(image_path_input)
