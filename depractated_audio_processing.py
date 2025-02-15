import openai
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import soundfile as sf  # Required for MP3 playback

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Correct way to initialize client

def text_to_speech(text, output_file="output.mp3"):
    response = client.audio.speech.create(  # Corrected API call
        model="tts-1",
        input=text,
        voice="alloy"
    )

    with open(output_file, "wb") as f:
        f.write(response.content)  # Correct way to handle response

    print(f"TTS audio saved to {output_file}")
    return output_file

def play_audio(file_path):
    """Play the audio file using sounddevice."""
    data, samplerate = sf.read(file_path, dtype='int16')
    sd.play(data, samplerate)
    sd.wait()

def record_audio(duration=5, samplerate=16000, output_file=None):
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    print("Recording finished.")
    
    if output_file is None:
        output_file = tempfile.mktemp(suffix=".wav")
    
    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    print(f"Audio saved to {output_file}")
    return output_file

def speech_to_text(audio_file):
    with open(audio_file, "rb") as f:
        response = client.audio.transcriptions.create(  # Corrected API call
            model="whisper-1",
            file=f
        )
    
    return response.text  # New API format returns `.text`, not a dictionary

def chat_with_gpt4(prompt, model="gpt-4o"):
    """Sends user input to GPT-4 and returns the response."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content  # Extracts the response text

if __name__ == "__main__":
    # Example TTS
    text = "Hello, this is a test of OpenAI's text-to-speech system. How may I help you today?"
    audio_file = text_to_speech(text)
    play_audio(audio_file)
    for i in range(4):
        # Example STT
        recorded_file = record_audio(duration=5)
        play_audio(recorded_file)
        transcribed_text = speech_to_text(recorded_file)
        print("Transcribed text:", transcribed_text)
        response = chat_with_gpt4(transcribed_text)
        audio_file = text_to_speech(response)
        play_audio(audio_file)
    
    # Cleanup temporary files
    os.remove(recorded_file)
    os.remove(audio_file)
