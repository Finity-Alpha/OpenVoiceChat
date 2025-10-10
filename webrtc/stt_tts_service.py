from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
import numpy as np
import torch
from openvoicechat.stt.stt_hf import Ear_hf
from openvoicechat.tts.tts_kokoro import Mouth_kokoro

# Initialize models globally
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
stt_model = None
tts_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the STT and TTS models on startup"""
    global stt_model, tts_model
    print(f"Loading models on device: {device}")

    # Load STT model
    stt_model = Ear_hf(
        model_id="openai/whisper-tiny.en",
        device=device,
        silence_seconds=1.5,
        listen_interruptions=False,
    )
    print("STT model loaded successfully")

    # Load TTS model
    tts_model = Mouth_kokoro(
        lang_code="a",  # American English
        voice="af_heart",
        speed=1.0,
        device=device,
        player=None,  # We won't use the audio player
        wait=False,
    )
    print(tts_model.sample_rate)
    print("TTS model loaded successfully")

    yield
    # Cleanup would go here if needed


app = FastAPI(title="OpenVoiceChat STT+TTS Service", version="1.0.0", lifespan=lifespan)


@app.post("/transcribe")
async def transcribe_audio(request: Request):
    """
    Transcribe numpy array buffer to text

    Args:
        request: Raw request containing numpy array buffer

    Returns:
        JSON response with transcription
    """
    try:
        # Read raw bytes from request body
        audio_bytes = await request.body()

        # Convert bytes back to numpy array
        # Assuming the array was sent as float32 bytes
        audio_data = np.frombuffer(audio_bytes, dtype=np.float32)

        # Validate array is not empty
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio data received")

        # Transcribe using OpenVoiceChat STT
        transcription = stt_model.transcribe(audio_data)

        return JSONResponse(
            status_code=200,
            content={
                "transcription": transcription,
                "success": True,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/synthesize")
async def synthesize_text(request: Request):
    """
    Synthesize text to audio using TTS

    Args:
        request: Request body containing text as plain string

    Returns:
        Audio data as bytes (numpy array in float32 format)
    """
    try:
        # Read text from request body
        text_bytes = await request.body()
        text = text_bytes.decode("utf-8").strip()

        # Validate text is not empty
        if not text:
            raise HTTPException(status_code=400, detail="Empty text received")

        # Generate audio using OpenVoiceChat TTS
        audio_data = np.array(tts_model.run_tts(text), dtype=np.float32)

        # Convert numpy array to bytes
        audio_bytes = audio_data.astype(np.float32).tobytes()

        return Response(
            content=audio_bytes,
            media_type="application/octet-stream",
            headers={
                "X-Success": "true",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Speech synthesis failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "stt_model_loaded": stt_model is not None,
        "tts_model_loaded": tts_model is not None,
        "device": device,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
