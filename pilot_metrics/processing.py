from typing import Any

from .models import DailyCopilotStats


def flatten_copilot_data(
    daily_stats: list[DailyCopilotStats],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Flattens nested Copilot data into flat dictionaries for easier analysis.

    Returns:
        Tuple of (completions_data, chats_data) where each is a list
        of flat dictionaries
    """
    completions = []
    chats = []

    for daily_stat in daily_stats:
        date = daily_stat.date

        # Process IDE code completions
        for editor in daily_stat.copilot_ide_code_completions.editors:
            for model in editor.models:
                for language in model.languages:
                    completion_record = {
                        "date": date,
                        "editor": editor.name,
                        "model": model.name,
                        "is_custom_model": model.is_custom_model,
                        "language": language.name,
                        "total_engaged_users": language.total_engaged_users,
                        "total_code_acceptances": language.total_code_acceptances,
                        "total_code_suggestions": language.total_code_suggestions,
                        "total_code_lines_accepted": language.total_code_lines_accepted,
                        "total_code_lines_suggested": (
                            language.total_code_lines_suggested
                        ),
                    }
                    completions.append(completion_record)

        # Process IDE chats
        for editor in daily_stat.copilot_ide_chat.editors:
            for model in editor.models:
                chat_record = {
                    "date": date,
                    "chat_type": "ide",
                    "editor": editor.name,
                    "model": model.name,
                    "is_custom_model": model.is_custom_model,
                    "total_chats": model.total_chats,
                    "total_engaged_users": model.total_engaged_users,
                    "total_chat_copy_events": model.total_chat_copy_events or 0,
                    "total_chat_insertion_events": model.total_chat_insertion_events
                    or 0,
                }
                chats.append(chat_record)

        # Process dotcom chats
        for model in daily_stat.copilot_dotcom_chat.models:
            chat_record = {
                "date": date,
                "chat_type": "dotcom",
                "editor": None,
                "model": model.name,
                "is_custom_model": model.is_custom_model,
                "total_chats": model.total_chats,
                "total_engaged_users": model.total_engaged_users,
                "total_chat_copy_events": model.total_chat_copy_events or 0,
                "total_chat_insertion_events": model.total_chat_insertion_events or 0,
            }
            chats.append(chat_record)

    return completions, chats
