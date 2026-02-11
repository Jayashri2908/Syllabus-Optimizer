import pytest
from src.ai.openrouter_model import OpenRouterModel
from unittest.mock import MagicMock, patch

@patch('src.ai.openrouter_model.OpenAI')
def test_openrouter_params_passing(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    model = OpenRouterModel(config={'api_key': 'test_key'})
    model.generate(
        prompt="test",
        temperature=0.3,
        max_tokens=4000,
        top_p=0.85,
        top_k=40,
        frequency_penalty=0.2,
        presence_penalty=0.1,
        repetition_penalty=1.15
    )
    
    # Check if create was called with correct params
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['temperature'] == 0.3
    assert kwargs['max_tokens'] == 4000
    assert kwargs['top_p'] == 0.85
    assert kwargs['frequency_penalty'] == 0.2
    assert kwargs['presence_penalty'] == 0.1
    assert kwargs['extra_body']['top_k'] == 40
    assert kwargs['extra_body']['repetition_penalty'] == 1.15
