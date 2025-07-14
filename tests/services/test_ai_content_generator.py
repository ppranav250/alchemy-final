import pytest
from unittest.mock import MagicMock
from api.services.ai_content_generator import generate_and_parse_script

# A mock response from the Claude API
FAKE_CLAUDE_RESPONSE = """
<video_prompt>
[SCENE 1]
- A shot of a brain.
</video_prompt>

<narration_script>
[SCENE 1]
"This is the first line."
"This is the second line."
</narration_script>
"""

# A malformed response missing the narration script
MALFORMED_CLAUDE_RESPONSE = """
<video_prompt>
[SCENE 1]
- A shot of a brain.
</video_prompt>
"""

@pytest.fixture
def mock_anthropic_client(mocker):
    """Mocks the Anthropic client and its messages.create method."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_content = MagicMock()
    mock_content.text = FAKE_CLAUDE_RESPONSE
    mock_message.content = [mock_content]
    mock_client.messages.create.return_value = mock_message
    mocker.patch('anthropic.Anthropic', return_value=mock_client)
    return mock_client

def test_generate_and_parse_script_success(mock_anthropic_client):
    """Tests successful generation and parsing of the script."""
    result = generate_and_parse_script('Some paper text.')

    assert result['success'] is True
    assert '[SCENE 1]' in result['video_prompt']
    assert len(result['narration_lines']) == 2
    assert result['narration_lines'][0] == '"This is the first line."' 

def test_generate_and_parse_script_malformed_response(mock_anthropic_client):
    """Tests handling of a malformed response from Claude."""
    # Configure the mock to return the malformed response for this test
    mock_anthropic_client.messages.create.return_value.content[0].text = MALFORMED_CLAUDE_RESPONSE

    result = generate_and_parse_script('Some paper text.')

    assert 'error' in result
    assert 'Failed to parse' in result['error']

def test_generate_and_parse_script_api_error(mock_anthropic_client):
    """Tests handling of an API error during the call to Claude."""
    # Configure the mock to raise an exception
    mock_anthropic_client.messages.create.side_effect = Exception('API Connection Error')

    result = generate_and_parse_script('Some paper text.')

    assert 'error' in result
    assert 'Claude API error' in result['error']
