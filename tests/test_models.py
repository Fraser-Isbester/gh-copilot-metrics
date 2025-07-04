import pytest
from pilot_metrics.models import (
    LanguageMetrics,
    ChatModel,
    CopilotData,
    DailyCopilotStats,
    CopilotIdeCodeCompletions,
    CopilotIdeChat,
    CopilotDotComChat,
    CopilotDotComPullRequests,
)


def test_language_metrics():
    """Test LanguageMetrics model validation."""
    data = {
        "name": "python",
        "total_engaged_users": 10,
        "total_code_acceptances": 100,
        "total_code_suggestions": 150,
        "total_code_lines_accepted": 200,
        "total_code_lines_suggested": 300,
    }
    metrics = LanguageMetrics(**data)
    assert metrics.name == "python"
    assert metrics.total_engaged_users == 10
    assert metrics.total_code_acceptances == 100


def test_language_metrics_defaults():
    """Test LanguageMetrics with default values."""
    metrics = LanguageMetrics(name="javascript")
    assert metrics.name == "javascript"
    assert metrics.total_engaged_users == 0
    assert metrics.total_code_acceptances == 0


def test_chat_model():
    """Test ChatModel validation."""
    data = {
        "name": "gpt-4",
        "is_custom_model": False,
        "total_chats": 50,
        "total_engaged_users": 25,
        "total_chat_copy_events": 10,
        "total_chat_insertion_events": 15,
    }
    model = ChatModel(**data)
    assert model.name == "gpt-4"
    assert model.is_custom_model is False
    assert model.total_chats == 50


def test_copilot_data_validation():
    """Test CopilotData root model validation."""
    sample_data = [
        {
            "date": "2024-01-15",
            "total_active_users": 100,
            "total_engaged_users": 80,
            "copilot_ide_code_completions": {
                "total_engaged_users": 60,
                "editors": [],
                "languages": [],
            },
            "copilot_ide_chat": {
                "total_engaged_users": 30,
                "editors": [],
            },
            "copilot_dotcom_chat": {
                "total_engaged_users": 20,
                "models": [],
            },
            "copilot_dotcom_pull_requests": {
                "total_engaged_users": 15,
                "repositories": [],
            },
        }
    ]
    
    copilot_data = CopilotData.model_validate(sample_data)
    assert len(copilot_data.root) == 1
    assert copilot_data.root[0].date == "2024-01-15"
    assert copilot_data.root[0].total_active_users == 100


def test_daily_copilot_stats():
    """Test DailyCopilotStats model."""
    data = {
        "date": "2024-01-15",
        "total_active_users": 100,
        "total_engaged_users": 80,
        "copilot_ide_code_completions": {
            "total_engaged_users": 60,
            "editors": [],
            "languages": [],
        },
        "copilot_ide_chat": {
            "total_engaged_users": 30,
            "editors": [],
        },
        "copilot_dotcom_chat": {
            "total_engaged_users": 20,
            "models": [],
        },
        "copilot_dotcom_pull_requests": {
            "total_engaged_users": 15,
            "repositories": [],
        },
    }
    
    stats = DailyCopilotStats(**data)
    assert stats.date == "2024-01-15"
    assert stats.total_active_users == 100
    assert stats.copilot_ide_code_completions.total_engaged_users == 60


def test_invalid_data():
    """Test that invalid data raises validation errors."""
    with pytest.raises(Exception):  # Pydantic validation error
        LanguageMetrics(name=123)  # name should be string
    
    with pytest.raises(Exception):
        ChatModel(name="test", is_custom_model="not_boolean")  # should be boolean