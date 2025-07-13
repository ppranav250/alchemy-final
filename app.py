from flask import Flask, render_template, request, jsonify
import os
import requests
import fitz  # PyMuPDF
import anthropic
import subprocess
from lmnt.api import Lmnt
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ensure you have set these in your .env file
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LMNT_API_KEY = os.getenv("LMNT_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
lmnt_client = Lmnt(LMNT_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_paper():
    data = request.get_json()
    paper_url = data.get('url')

    if not paper_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # 1. Web Scraping: Get the research paper
        response = requests.get(paper_url)
        response.raise_for_status() # Raise an exception for bad status codes

        # Assuming the paper is a PDF
        pdf_content = response.content
        
        # 2. Parsing: Parse the paper
        text_content = ""
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                text_content += page.get_text()

        # 3. In-Context Learning Prompt for Claude
        prompt = f"""\n\nHuman: You are Grant Sanderson, the creator of the YouTube channel 3blue1brown. Your task is to create an educational, visually-driven script for a video explaining the core concepts of a research paper. The script should be written in a way that is accessible to a broad audience, using analogies and intuitive explanations, just like a 3blue1brown video. The final output must be a Python script using the 'manim' library. The script should generate the animations you describe.

Here is the content of the research paper:
<research_paper>
{text_content[:15000]} 
</research_paper>

Your script should be structured as follows:
1.  A brief, engaging introduction that hooks the viewer.
2.  A clear explanation of the problem the paper is trying to solve.
3.  A step-by-step breakdown of the paper's methodology, using visual analogies that can be animated with manim.
4.  A demonstration of the results, again, focusing on visual intuition.
5.  A concluding summary that reinforces the main takeaways.

When writing the manim script, imagine you are directing the video. Use comments in the code to describe the narration that would accompany each scene. The narration should be in your signature style: calm, clear, and insightful.

Here is an example of how you might structure a scene in the manim script:

```python
from manim import *

class PaperExplanationScene(Scene):
    def construct(self):
        # Narration: "Let's start with the fundamental building block of this idea..."
        title = Text("The Core Idea").to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # ... manim code for the animation ...
```

Now, based on the provided research paper, generate the complete manim Python script. The script should be self-contained and ready to run. The class name in the script must be `GeneratedScene`. Do not include any introductory text before the python code block. The output should be only the python script itself, enclosed in ```python and ```.

Assistant:"""

        # 4. Generate Manim Script with Claude
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ).content[0].text

        # Extract the python code from the response
        manim_script_content = message.strip().replace('```python', '').replace('```', '').strip()

        # Save the generated manim script to a file
        script_path = 'generated_scene.py'
        with open(script_path, 'w') as f:
            f.write(manim_script_content)

        # 5. Run manim to generate the video
        # Note: Manim execution can be complex. This is a simplified approach.
        # It assumes manim is in the system's PATH.
        # The '-ql' flag is for low quality, which is faster.
        result = subprocess.run(['manim', '-ql', script_path, 'GeneratedScene'], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'error': 'Manim execution failed', 'details': result.stderr}), 500

        silent_video_path = os.path.join('media', 'videos', 'generated_scene', '480p15', 'GeneratedScene.mp4')

        # 6. Voice Generation with LMNT and audio stitching
        import re

        # 6.1 Parse narration from the script
        narration_comments = re.findall(r'# Narration: "(.*?)"', manim_script_content)

        if not narration_comments:
            # If no narration, just return the silent video
            return jsonify({'video_path': silent_video_path})

        # 6.2 Generate audio for each line
        audio_files = []
        audio_dir = os.path.join('media', 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        for i, text in enumerate(narration_comments):
            try:
                # Using 'grant' voice to match the 3b1b style requested in the prompt
                # Note: The 'grant' voice may not exist. You can list available voices with `lmnt_client.get_voices()`
                # and replace 'grant' with a real voice ID like 'lily' or 'james'.
                audio_response = lmnt_client.synthesize(text, 'lily') # Changed to a known good voice
                audio_data = audio_response['audio']
                filename = f"narration_{i}.mp3"
                filepath = os.path.join(audio_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(audio_data)
                audio_files.append(filepath)
            except Exception as e:
                print(f"LMNT synthesis failed for line: {text}. Error: {e}")

        if not audio_files:
            # No audio was successfully generated, return silent video
            return jsonify({'video_path': silent_video_path})

        # 6.3 Stitch audio files
        combined_audio = AudioSegment.empty()
        for audio_file in audio_files:
            segment = AudioSegment.from_mp3(audio_file)
            combined_audio += segment

        stitched_audio_path = os.path.join(audio_dir, 'final_narration.mp3')
        combined_audio.export(stitched_audio_path, format="mp3")

        # 6.4 Combine video and audio with ffmpeg
        final_video_path = os.path.join(os.path.dirname(silent_video_path), 'GeneratedScene_narrated.mp4')
        
        # Ensure ffmpeg is in the system's PATH
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-i', silent_video_path,
            '-i', stitched_audio_path,
            '-c:v', 'copy',  # Copy video stream without re-encoding
            '-c:a', 'aac',   # Re-encode audio to AAC
            '-shortest',     # Finish encoding when the shortest input stream ends
            final_video_path
        ]
        ffmpeg_result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

        if ffmpeg_result.returncode != 0:
            return jsonify({'error': 'FFmpeg execution failed', 'details': ffmpeg_result.stderr}), 500

        # 6.5 Clean up intermediate audio files
        for audio_file in audio_files:
            os.remove(audio_file)
        os.remove(stitched_audio_path)

        # Return the path to the final narrated video
        return jsonify({'video_path': final_video_path})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Failed to fetch paper: {e}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
