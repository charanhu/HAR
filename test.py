import ollama

response = ollama.chat(
    model="llama3.2-vision",
    messages=[
        {
            "role": "user",
            "content": "whats in the image?",
            "images": ["/Users/charan/VSCode/GITHUB/HAR/test2.jpg"],
        }
    ],
    stream=True,
)

for r in response:
    print(r["message"]["content"])
