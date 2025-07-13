from .services import paper_parser, ai_content_generator, audio_synthesizer

def process_research_paper(paper_url: str) -> dict:
    """
    Orchestrates the entire workflow from paper URL to final assets.

    Args:
        paper_url: The public URL to the PDF of the research paper.

    Returns:
        A dictionary containing the final results or an error.
    """
    # Step 1: Fetch and parse the paper content
    parser_result = paper_parser.parse_paper_from_url(paper_url)
    if 'error' in parser_result:
        return parser_result
    
    # Step 2: Generate video prompt and narration script from the content
    ai_result = ai_content_generator.generate_and_parse_script(parser_result['text_content'])
    if 'error' in ai_result:
        return ai_result

    # Step 3: Synthesize the narration audio
    audio_result = audio_synthesizer.synthesize_and_stitch_audio(ai_result['narration_lines'])
    if 'error' in audio_result:
        return audio_result

    # Step 4: Compile the final successful response
    return {
        'success': True,
        'message': 'Video generation is not yet available. Here is the generated audio and the prompt for Veo.',
        'audio_path': audio_result['audio_path'],
        'video_prompt': ai_result['video_prompt']
    }
