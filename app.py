from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import ollama
from typing import Generator
from contextlib import asynccontextmanager

app = FastAPI()

MODEL_NAME = "llama3.2-vision"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to manage startup and shutdown events.
    """
    # Startup: Initialize or preload the model
    print(f"Loading model '{MODEL_NAME}' for inference...")
    # If Ollama requires explicit model setup or initialization, place it here.
    # For example, you might establish a connection or load model weights.
    # This example assumes Ollama manages the model lifecycle implicitly.
    print(f"Model '{MODEL_NAME}' is ready for inference.")
    
    yield  # Control is passed to the application
    
    # Shutdown: Perform any necessary cleanup
    print(f"Shutting down. Model '{MODEL_NAME}' will be unloaded if necessary.")
    # Add any shutdown logic if required
    # For example, closing connections or freeing resources

# Assign the lifespan context manager to the FastAPI app
app.router.lifespan = lifespan

def stream_inference_response(image_bytes: bytes) -> Generator[str, None, None]:
    """
    Generator function to stream model inference output.
    """
    try:
        # Run inference using the Ollama model
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": "What's in the image?",
                    "images": [image_bytes],  # Pass image as bytes
                }
            ],
            stream=True,
        )
        # Stream the response content
        for r in response:
            if "message" in r and "content" in r["message"]:
                yield r["message"]["content"] + "\n"
            else:
                yield "Received an unexpected response format.\n"
    except Exception as e:
        yield f"Error during inference: {str(e)}\n"

@app.post("/infer")
async def infer_image(file: UploadFile = File(...)):
    """
    Receives an image via a POST request, runs inference, and streams the output.
    """
    try:
        # Read the uploaded file as bytes
        image_bytes = await file.read()
        
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        # Optionally, validate the image format here (e.g., check MIME type)
        # mime_type = file.content_type
        # if mime_type not in ["image/jpeg", "image/png"]:
        #     raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        print(f"Image received: {file.filename}, size: {len(image_bytes)} bytes")
        
        # Stream the output
        return StreamingResponse(
            stream_inference_response(image_bytes),
            media_type="text/plain"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")
