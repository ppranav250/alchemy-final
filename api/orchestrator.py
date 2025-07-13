import logging
from .services import paper_parser, ai_content_generator, audio_synthesizer

logger = logging.getLogger(__name__)

def process_research_paper(paper_url: str) -> dict:
    """
    Orchestrates the entire workflow from paper URL to final assets.

    Args:
        paper_url: The public URL to the PDF of the research paper.

    Returns:
        A dictionary containing the final results or an error.
    """
    logger.info(f"Starting research paper processing for URL: {paper_url}")
    # Step 1: Fetch and parse the paper content
    logger.info("Parsing paper content...")
    parser_result = paper_parser.parse_paper_from_url(paper_url)
    if 'error' in parser_result:
        logger.error(f"Paper parsing failed: {parser_result['error']}")
        return parser_result
    logger.info("Paper content parsed successfully.")
    
    # Step 2: Generate video prompt and narration script from the content
    logger.info("Generating AI content...")
    ai_result = ai_content_generator.generate_and_parse_script(parser_result['text_content'])
    if 'error' in ai_result:
        logger.error(f"AI content generation failed: {ai_result['error']}")
        return ai_result
    logger.info(f"AI content generated. Narration contains {len(ai_result['narration_lines'])} lines.")

    # Step 3: Synthesize the narration audio
    logger.info("Synthesizing audio...")
    audio_result = audio_synthesizer.synthesize_and_stitch_audio(ai_result['narration_lines'])
    if 'error' in audio_result:
        logger.error(f"Audio synthesis failed: {audio_result['error']}")
        return audio_result
    logger.info(f"Audio synthesized and saved to {audio_result['audio_path']}")

    # Step 4: Compile the final successful response
    logger.info("Workflow completed successfully.")
    return {
        'success': True,
        'message': 'Video generation is not yet available. Here is the generated audio and the prompt for Veo.',
        'audio_path': audio_result['audio_path'],
        'video_prompt': ai_result['video_prompt']
    }
