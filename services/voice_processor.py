import whisper
import soundfile as sf
import os
import tempfile
from config import Config


class VoiceProcessor:
    def __init__(self):
        """Initialize the voice processor with Whisper model"""
        try:
            # Use base model for better performance vs accuracy trade-off
            self.model = whisper.load_model("base")
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None

    def speech_to_text(self, audio_path, language='en'):
        """Convert speech audio file to text

        Args:
            audio_path (str): Path to the audio file
            language (str): Language code for transcription (e.g., 'en', 'vi')
        """
        if not self.model:
            return "Audio transcription unavailable - model not loaded"

        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                return "Audio file not found"

            # Load and process audio
            data, samplerate = sf.read(audio_path)

            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = data.mean(axis=1)

            # Resample to 16kHz if needed (Whisper's expected sample rate)
            if samplerate != 16000:
                # Create temporary file with correct sample rate
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp_file:
                    temp_path = temp_file.name
                    # Simple resampling (for production, consider using librosa)
                    step = samplerate // 16000
                    resampled_data = data[::step] if step > 1 else data
                    sf.write(temp_path, resampled_data, 16000)
                    audio_path = temp_path

            # Transcribe audio with specified language
            # If language is None or empty, let Whisper auto-detect
            if language and language.strip():
                result = self.model.transcribe(audio_path, language=language)
            else:
                result = self.model.transcribe(audio_path)
            transcribed_text = result["text"].strip()

            # Clean up temporary file if created
            if samplerate != 16000 and os.path.exists(temp_path):
                os.unlink(temp_path)

            return (
                transcribed_text if transcribed_text else "Could not transcribe audio"
            )

        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Transcription failed: {str(e)}"

    def validate_audio_file(self, file_path):
        """Validate if the audio file is readable"""
        try:
            data, samplerate = sf.read(file_path)
            return len(data) > 0 and samplerate > 0
        except Exception as e:
            print(f"Audio validation error: {e}")
            return False

    def get_audio_duration(self, file_path):
        """Get duration of audio file in seconds"""
        try:
            data, samplerate = sf.read(file_path)
            return len(data) / samplerate
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0

    def text_to_speech_placeholder(self, text):
        """Placeholder for text-to-speech functionality"""
        # This could be implemented with a TTS service like gTTS or Azure Speech
        print(f"TTS: {text}")
        return "TTS not implemented"

