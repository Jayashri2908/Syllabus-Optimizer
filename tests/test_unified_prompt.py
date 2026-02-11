import pytest
from src.optimization.content_optimizer import ContentOptimizer
from unittest.mock import MagicMock, call

@pytest.fixture
def mock_ai():
    mock = MagicMock()
    mock.generate_json.return_value = {
        "optimized_syllabus": {
            "course_title": "Optimized Data Structures",
            "course_code": "CS201",
            "learning_outcomes": [{"code": "CO1", "description": "Apply stacks", "bloom_level": "Apply"}],
            "units": [{"unit_number": 1, "title": "Stacks", "hours": 5, "topics": ["Push", "Pop"]}]
        },
        "changes_summary": ["Rewrote outcomes"],
        "bloom_distribution": {"apply": 100},
        "rationale": "Better alignment"
    }
    return mock

def test_optimize_full_syllabus_structure(mock_ai):
    optimizer = ContentOptimizer(model_manager=mock_ai)
    sample_data = {"course_title": "Old Course", "units": []}
    
    result = optimizer.optimize_full_syllabus(sample_data)
    
    assert "optimized_syllabus" in result
    assert "changes_summary" in result
    assert "bloom_distribution" in result
    assert result["optimized_syllabus"]["course_title"] == "Optimized Data Structures"


def test_optimize_passes_correct_parameters(mock_ai):
    """Verify that the correct parameters are passed to generate_json (Issue #6)"""
    optimizer = ContentOptimizer(model_manager=mock_ai)
    sample_data = {"course_title": "Test Course", "units": []}
    
    optimizer.optimize_full_syllabus(sample_data)
    
    # Verify generate_json was called
    mock_ai.generate_json.assert_called_once()
    
    # Extract the call arguments
    call_kwargs = mock_ai.generate_json.call_args.kwargs
    
    # Verify key parameters are passed correctly
    assert call_kwargs['task_type'] == 'optimization'
    assert call_kwargs['temperature'] == 0.3
    assert call_kwargs['max_tokens'] == 4096
    assert call_kwargs['top_p'] == 0.85
    assert call_kwargs['top_k'] == 40
    assert call_kwargs['frequency_penalty'] == 0.2
    assert call_kwargs['presence_penalty'] == 0.1
    assert call_kwargs['repetition_penalty'] == 1.15
    
    # Verify prompt contains syllabus data
    assert 'Test Course' in call_kwargs['prompt']
