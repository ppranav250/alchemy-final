import os
from lmnt.api import Lmnt
from pydub import AudioSegment

def synthesize_and_stitch_audio(narration_lines: list) -> dict:
    """
    Synthesizes audio for a list of narration lines and stitches them together.

    Args:
        narration_lines: A list of strings, where each string is a line of narration.

    Returns:
        A dictionary containing the path to the final audio file, or an error.
    """
    try:
        lmnt_client = Lmnt(os.getenv("LMNT_API_KEY"))
        audio_files = []
        audio_dir = os.path.join('media', 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        for i, text in enumerate(narration_lines):
            try:
                audio_response = lmnt_client.synthesize(text, 'lily')
                audio_data = audio_response['audio']
                filename = f"narration_{i}.mp3"
                filepath = os.path.join(audio_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(audio_data)
                audio_files.append(filepath)
            except Exception as e:
                # Log the error but continue if possible
                print(f"LMNT synthesis failed for line: '{text}'. Error: {e}")

        if not audio_files:
            return {'error': 'Audio synthesis failed for all narration lines.'}

        combined_audio = AudioSegment.empty()
        for audio_file in audio_files:
            segment = AudioSegment.from_mp3(audio_file)
            combined_audio += segment

        stitched_audio_path = os.path.join(audio_dir, 'final_narration.mp3')
        combined_audio.export(stitched_audio_path, format="mp3")

        # Clean up intermediate files
        for audio_file in audio_files:
            os.remove(audio_file)

        return {'success': True, 'audio_path': stitched_audio_path}

    except Exception as e:
        return {'error': f"Audio processing error: {e}"}
