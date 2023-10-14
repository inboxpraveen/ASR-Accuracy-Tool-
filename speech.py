import torch
import torchaudio

from transformers import (
    Wav2Vec2ForCTC,
    Wav2Vec2Tokenizer
)
from transformers import (
    WhisperProcessor, 
    WhisperForConditionalGeneration
)

def load_model_and_tokenizer(model_name):
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if "whisper" in model_name:
            processor = WhisperProcessor.from_pretrained(model_name)
            model = WhisperForConditionalGeneration.from_pretrained(model_name)
            model.config.forced_decoder_ids = None
            model.eval()
            model.to(device)
            return model, processor, device

        elif "wav2vec2" in model_name:
            model = Wav2Vec2ForCTC.from_pretrained(model_name)
            tokenizer = Wav2Vec2Tokenizer.from_pretrained(model_name)
            model.eval()
            model.to(device)
            return model, tokenizer, device
        else:
            return None, None, device
    except Exception:
        return None, None, None


MODEL_MAPPING = {
    "wav2vec2-base-960h": "facebook/wav2vec2-base-960h",
    "wav2vec2-large-960h": "facebook/wav2vec2-large-960h",
    
    "whisper-tiny": "openai/whisper-tiny",
    "whisper-base": "openai/whisper-base",
    "whisper-small": "openai/whisper-small",
    "whisper-medium": "openai/whisper-medium",
    "whisper-large": "openai/whisper-large",
}


def transcribe(model, tokenizer, device, input_path, model_name = "whisper-tiny"):

    waveform, rate = torchaudio.load(input_path, normalize=True)
    transcription = ""
    
    if "whisper" in model_name:
        input_features = tokenizer(waveform.squeeze().numpy(), sampling_rate=rate, return_tensors="pt").input_features.to(device)
        predicted_ids = model.generate(input_features)
        transcription = tokenizer.batch_decode(predicted_ids, skip_special_tokens=True)
        if isinstance(transcription, list):
            transcription = transcription[0]
    
    elif "wav2vec2" in model_name:
        input_values = tokenizer(waveform.squeeze().numpy(), return_tensors="pt", padding="longest").input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(predicted_ids)

    print("Transcription of current chunk : ", transcription)
    return transcription


def clear_memory(model, tokenizer):
    print("Trying to clear memory")
    del model, tokenizer
    print("Cleared out memory successfully.")


if __name__ == "__main__":
    # transcriber = SpeechToTextTranscriber("wav2vec2-large-960h")
    # text = transcriber.transcribe("path/to/your/audio/file.wav")
    # print(f"Transcribed Text: {text}")
    # transcriber.clear_memory("wav2vec2-large-960h")
    ...
