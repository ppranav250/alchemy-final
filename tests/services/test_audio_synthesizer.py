import pytest
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from api.services.audio_synthesizer import synthesize_and_stitch_audio

@pytest.fixture
def mock_speech_client(mocker):
    """Mocks the async Speech client and its synthesize method."""
    mock_speech_instance = AsyncMock()
    mock_speech_instance.synthesize.return_value = {'audio': b'fake_audio_data'}
    
    # Mock the class and its async context manager
    mock_speech_class = MagicMock()
    mock_speech_class.return_value.__aenter__.return_value = mock_speech_instance
    mocker.patch('api.services.audio_synthesizer.Speech', mock_speech_class)
    return mock_speech_instance

@patch('os.makedirs')
@patch('os.remove')
@patch('pydub.AudioSegment.from_mp3')
@patch('pydub.AudioSegment.empty')
@patch('builtins.open')
def test_synthesize_and_stitch_audio_success(
    mock_open, mock_empty, mock_from_mp3, mock_remove, mock_makedirs, mock_speech_client
):
    """Tests the successful synthesis and stitching of audio files."""
    # Mock AudioSegment methods to avoid real audio processing
    mock_segment = MagicMock()
    mock_from_mp3.return_value = mock_segment
    mock_combined = MagicMock()
    # Ensure that in-place addition (+=) returns the same mock object
    mock_combined.__iadd__.return_value = mock_combined
    mock_empty.return_value = mock_combined

    narration_lines = ["Hello.", "World."]
    result = synthesize_and_stitch_audio(narration_lines)

    assert result['success'] is True
    assert 'final_narration.mp3' in result['audio_path']
    assert mock_speech_client.synthesize.call_count == 2
    assert mock_combined.export.call_count == 1
    assert mock_remove.call_count == 2 # Check that cleanup happens

def test_synthesize_and_stitch_audio_synthesis_fails(mock_speech_client):
    """Tests handling of a complete failure from the LMNT API."""
    mock_speech_client.synthesize.side_effect = Exception('API Error')

    narration_lines = ["Hello.", "World."]
    result = synthesize_and_stitch_audio(narration_lines)

    assert 'error' in result
    assert 'Audio synthesis failed for all narration lines' in result['error']

@patch('os.makedirs')
@patch('os.remove')
@patch('pydub.AudioSegment.from_mp3', side_effect=Exception('Pydub Error'))
@patch('builtins.open')
def test_synthesize_and_stitch_audio_processing_error(
    mock_open, mock_from_mp3, mock_remove, mock_makedirs, mock_speech_client
):
    """Tests handling of an error during audio processing (e.g., with pydub)."""
    narration_lines = ["Hello."]
    result = synthesize_and_stitch_audio(narration_lines)

    assert 'error' in result
    assert 'Audio processing error' in result['error']
