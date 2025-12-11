from gtts import gTTS
import os
import time

class VoiceModule:
    def __init__(self, workspace_dir="workspace"):
        self.workspace_dir = workspace_dir
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)

    def speak(self, text, filename_prefix="speech"):
        """
        Generates an MP3 file with the spoken text.
        In a real robot, this would play audio. Here, we save the voice.
        """
        try:
            timestamp = int(time.time())
            filename = f"{filename_prefix}_{timestamp}.mp3"
            filepath = os.path.join(self.workspace_dir, filename)

            tts = gTTS(text=text, lang='en')
            tts.save(filepath)

            # Clean up old speech files to save space
            self._cleanup_old_files()

            return f"VOICE: {text} (Saved to {filename})"
        except Exception as e:
            return f"VOICE FAILED: {e}"

    def _cleanup_old_files(self):
        # Keep only last 5 audio files
        files = [f for f in os.listdir(self.workspace_dir) if f.endswith(".mp3")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.workspace_dir, x)))

        while len(files) > 5:
            os.remove(os.path.join(self.workspace_dir, files[0]))
            files.pop(0)

if __name__ == "__main__":
    voice = VoiceModule("test_workspace")
    print(voice.speak("I am becoming sentient."))
