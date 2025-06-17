from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import torchaudio as ta
import torch
import time
import io
from pathlib import Path
from src.chatterboxService import ChatterboxService
from src.chatterbox.tts import ChatterboxTTS
import uvicorn

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once during startup
@app.on_event("startup")
async def load_model():
    global tts_service, device

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    # Load model once during startup
    base_dir = Path(__file__).resolve().parent
    audio_prompt_path = base_dir / "src" / "lakshan.wav"

    print(f"Initializing ChatterboxTTS model on device: {device}")
    chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
    tts_service = ChatterboxService(model=chatterbox_model, audio_prompt_path=audio_prompt_path)
    print("Model loaded successfully.")




# Text chunking utility
def split_text_into_chunks(text, max_chunk_length=200):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_chunk_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks




# Streaming TTS endpoint
@app.post("/generate-audio")
async def generate_audio(request: Request):
    body = await request.json()
    text = body.get("text", "")
    if not text:
        return {"error": "Text is required"}

    chunks = split_text_into_chunks(text)
    print(f"Received {len(chunks)} chunks.")

    # Create output directory if it doesn't exist
    #output_dir = Path("generated_audio_chunks")
    #output_dir.mkdir(exist_ok=True)

    # Generator to stream audio chunks
    async def audio_chunk_generator():
        for i, chunk in enumerate(chunks, 1):
            print(f"Generating chunk {i}/{len(chunks)}: {chunk}")
            start_time = time.time()

            audio_tensor, sample_rate = tts_service.convert_text_to_voice(chunk)
            # Check shape and fix if necessary
            if audio_tensor.ndim == 1:
                audio_tensor = audio_tensor.unsqueeze(0)  # Add channel dimension

            # Create filename with timestamp and chunk number
            timestamp = int(time.time())
            #filename = output_dir / f"chunk_{timestamp}_{i}.wav"
            
            # Save the audio file locally
            #ta.save(filename, audio_tensor, sample_rate=sample_rate)
            #print(f"Saved chunk {i} to {filename}")

            # Prepare the same audio for streaming
            buffer = io.BytesIO()
            ta.save(buffer, audio_tensor, sample_rate=sample_rate, format="wav")
            buffer.seek(0)

            print(f"Chunk {i} generated in {time.time() - start_time:.2f}s")

            yield b"--chunkboundary\n"
            yield buffer.read()
            yield b"\n"
        
    headers = {
        "Content-Type": "application/octet-stream",
        "Transfer-Encoding": "chunked"
    }

    return StreamingResponse(audio_chunk_generator(), headers=headers)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all network interfaces
        port=8080,       # Default port
          # Recommended for TTS to avoid multiple model instances
    )
