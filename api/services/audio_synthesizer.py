import os
import asyncio
from lmnt.api import Speech
from pydub import AudioSegment
from ..config import Config

def synthesize_and_stitch_audio(narration_lines: list) -> dict:
    """
    Synthesizes audio for a list of narration lines and stitches them together.

    Args:
        narration_lines: A list of strings, where each string is a line of narration.

    Returns:
        A dictionary containing the path to the final audio file, or an error.
    """
    async def _synthesize_async(lines):
        audio_files = []
        async with Speech(Config.LMNT_API_KEY) as speech:
            for i, text in enumerate(lines):
                try:
                    synthesis = await speech.synthesize(text, Config.LMNT_VOICE)
                    audio_data = synthesis['audio']
                    filename = f"narration_{i}.mp3"
                    filepath = os.path.join(audio_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(audio_data)
                    audio_files.append(filepath)
                except Exception as e:
                    print(f"LMNT synthesis failed for line: '{text}'. Error: {e}")
        return audio_files

    try:
        audio_dir = Config.AUDIO_DIR
        os.makedirs(audio_dir, exist_ok=True)

        audio_files = asyncio.run(_synthesize_async(narration_lines))

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
