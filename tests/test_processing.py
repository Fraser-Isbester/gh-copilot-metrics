import pytest
from pilot_metrics.processing import flatten_copilot_data
from pilot_metrics.models import DailyCopilotStats


def test_flatten_copilot_data_empty():
    """Test flattening with empty data."""
    completions, chats = flatten_copilot_data([])
    assert completions == []
    assert chats == []


def test_flatten_copilot_data_with_sample():
    """Test flattening with sample data."""
    sample_stats = [
        DailyCopilotStats(
            date="2024-01-15",
            total_active_users=100,
            total_engaged_users=80,
            copilot_ide_code_completions={
                "total_engaged_users": 60,
                "editors": [
                    {
                        "name": "vscode",
                        "total_engaged_users": 40,
                        "models": [
                            {
                                "name": "gpt-4",
                                "is_custom_model": False,
                                "total_engaged_users": 40,
                                "languages": [
                                    {
                                        "name": "python",
                                        "total_engaged_users": 20,
                                        "total_code_acceptances": 100,
                                        "total_code_suggestions": 150,
                                        "total_code_lines_accepted": 200,
                                        "total_code_lines_suggested": 300,
                                    }
                                ],
                            }
                        ],
                    }
                ],
                "languages": [],
            },
            copilot_ide_chat={
                "total_engaged_users": 30,
                "editors": [
                    {
                        "name": "vscode",
                        "total_engaged_users": 30,
                        "models": [
                            {
                                "name": "gpt-4",
                                "is_custom_model": False,
                                "total_chats": 50,
                                "total_engaged_users": 30,
                                "total_chat_copy_events": 10,
                                "total_chat_insertion_events": 15,
                            }
                        ],
                    }
                ],
            },
            copilot_dotcom_chat={
                "total_engaged_users": 20,
                "models": [
                    {
                        "name": "gpt-4",
                        "is_custom_model": False,
                        "total_chats": 25,
                        "total_engaged_users": 20,
                        "total_chat_copy_events": 5,
                        "total_chat_insertion_events": 8,
                    }
                ],
            },
            copilot_dotcom_pull_requests={
                "total_engaged_users": 15,
                "repositories": [],
            },
        )
    ]
    
    completions, chats = flatten_copilot_data(sample_stats)
    
    # Test completions data
    assert len(completions) == 1
    completion = completions[0]
    assert completion["date"] == "2024-01-15"
    assert completion["editor"] == "vscode"
    assert completion["model"] == "gpt-4"
    assert completion["language"] == "python"
    assert completion["total_code_acceptances"] == 100
    assert completion["total_code_lines_accepted"] == 200
    
    # Test chats data
    assert len(chats) == 2  # One IDE chat + one dotcom chat
    
    ide_chat = next(chat for chat in chats if chat["chat_type"] == "ide")
    assert ide_chat["date"] == "2024-01-15"
    assert ide_chat["editor"] == "vscode"
    assert ide_chat["model"] == "gpt-4"
    assert ide_chat["total_chats"] == 50
    assert ide_chat["total_chat_copy_events"] == 10
    
    dotcom_chat = next(chat for chat in chats if chat["chat_type"] == "dotcom")
    assert dotcom_chat["date"] == "2024-01-15"
    assert dotcom_chat["editor"] is None
    assert dotcom_chat["model"] == "gpt-4"
    assert dotcom_chat["total_chats"] == 25
    assert dotcom_chat["total_chat_copy_events"] == 5


def test_flatten_handles_none_values():
    """Test that flattening handles None values correctly."""
    sample_stats = [
        DailyCopilotStats(
            date="2024-01-15",
            total_active_users=100,
            total_engaged_users=80,
            copilot_ide_code_completions={
                "total_engaged_users": 0,
                "editors": [],
                "languages": [],
            },
            copilot_ide_chat={
                "total_engaged_users": 30,
                "editors": [
                    {
                        "name": "vscode",
                        "total_engaged_users": 30,
                        "models": [
                            {
                                "name": "gpt-4",
                                "is_custom_model": False,
                                "total_chats": 50,
                                "total_engaged_users": 30,
                                "total_chat_copy_events": None,  # Test None handling
                                "total_chat_insertion_events": None,
                            }
                        ],
                    }
                ],
            },
            copilot_dotcom_chat={"total_engaged_users": 0, "models": []},
            copilot_dotcom_pull_requests={"total_engaged_users": 0, "repositories": []},
        )
    ]
    
    completions, chats = flatten_copilot_data(sample_stats)
    
    assert len(completions) == 0  # No completion data
    assert len(chats) == 1  # One IDE chat
    
    chat = chats[0]
    assert chat["total_chat_copy_events"] == 0  # None converted to 0
    assert chat["total_chat_insertion_events"] == 0  # None converted to 0