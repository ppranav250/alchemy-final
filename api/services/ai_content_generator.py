import os
import re
import anthropic

def generate_and_parse_script(text_content: str) -> dict:
    """
    Generates a video prompt and narration script from text using Claude.

    Args:
        text_content: The text content of the research paper.

    Returns:
        A dictionary containing the video prompt and narration lines, or an error.
    """
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        prompt = f"""\n\nHuman: You are an expert science communicator, like Grant Sanderson of 3blue1brown. Your task is to analyze a research paper and generate two things:
1. A detailed, scene-by-scene prompt for a generative text-to-video AI model like Google Veo. This prompt should describe a visually stunning, cinematic, and educational video that explains the paper's core concepts. Describe camera angles, lighting, and visual styles (e.g., 'photorealistic', 'sci-fi UI', 'abstract data visualization').
2. A clear and insightful narration script that will be spoken over the video.

Here is the content of the research paper:
<research_paper>
{text_content[:15000]}
</research_paper>

Structure your response as follows, using the exact tags:

<video_prompt>
[SCENE 1]
- A wide, establishing shot of a digital brain, neural pathways glowing with activity. Camera slowly zooms in. Style: photorealistic, cinematic, blue and gold lighting.
- Text overlay: 'The Challenge of...' (from paper's title)

[SCENE 2]
- A visual metaphor of the core problem. Describe the animation (e.g., 'data points represented as chaotic, swirling particles that slowly organize into a coherent structure').
- ... and so on for the entire video.
</video_prompt>

<narration_script>
[SCENE 1]
"In the vast landscape of artificial intelligence, one challenge has remained particularly elusive..."

[SCENE 2]
"Imagine trying to find a single, meaningful pattern in a storm of near-infinite data. This is the problem that researchers..."

- ... and so on for the entire script, with each line corresponding to a scene in the video prompt.
</narration_script>

Now, generate the <video_prompt> and <narration_script> for the provided research paper.

Assistant:"""

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ).content[0].text

        video_prompt_match = re.search(r'<video_prompt>(.*?)</video_prompt>', message, re.DOTALL)
        narration_script_match = re.search(r'<narration_script>(.*?)</narration_script>', message, re.DOTALL)

        if not video_prompt_match or not narration_script_match:
            return {'error': 'Failed to parse video prompt or narration from Claude response'}

        video_prompt = video_prompt_match.group(1).strip()
        narration_script = narration_script_match.group(1).strip()
        narration_lines = [line.strip() for line in narration_script.split('\n') if line.strip() and not line.startswith('[SCENE')]

        if not narration_lines:
            return {'error': 'No narration lines found in the script from Claude'}

        return {
            'success': True,
            'video_prompt': video_prompt,
            'narration_lines': narration_lines
        }

    except Exception as e:
        return {'error': f"Claude API error: {e}"}
