import json
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest
from typer.testing import CliRunner

from pilot_metrics.main import app, load_data


def test_load_data_from_file():
    """Test loading data from a file."""
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
            "copilot_ide_chat": {"total_engaged_users": 30, "editors": []},
            "copilot_dotcom_chat": {"total_engaged_users": 20, "models": []},
            "copilot_dotcom_pull_requests": {
                "total_engaged_users": 15,
                "repositories": [],
            },
        }
    ]

    mock_file_content = json.dumps(sample_data)

    with (
        patch("builtins.open", mock_open(read_data=mock_file_content)),
        patch("pilot_metrics.main.console.print") as mock_print,
    ):
        result = load_data("test_file.json")

        assert len(result) == 1
        assert result[0].date == "2024-01-15"
        mock_print.assert_any_call("[cyan]Reading data from 'test_file.json'...[/cyan]")


def test_load_data_from_stdin():
    """Test loading data from stdin."""
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
            "copilot_ide_chat": {"total_engaged_users": 30, "editors": []},
            "copilot_dotcom_chat": {"total_engaged_users": 20, "models": []},
            "copilot_dotcom_pull_requests": {
                "total_engaged_users": 15,
                "repositories": [],
            },
        }
    ]

    mock_stdin = MagicMock()
    mock_stdin.read.return_value = json.dumps(sample_data)

    with (
        patch("sys.stdin", mock_stdin),
        patch("json.load", return_value=sample_data),
        patch("pilot_metrics.main.console.print") as mock_print,
    ):
        result = load_data("-")

        assert len(result) == 1
        assert result[0].date == "2024-01-15"
        mock_print.assert_any_call("[cyan]Reading data from stdin...[/cyan]")


def test_load_data_file_not_found():
    """Test handling of file not found error."""
    from click.exceptions import Exit

    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        patch("pilot_metrics.main.console.print") as mock_print,
        pytest.raises(Exit),
    ):
        load_data("nonexistent.json")

        mock_print.assert_any_call(
            "[bold red]Error: File 'nonexistent.json' not found.[/bold red]"
        )


def test_load_data_invalid_json():
    """Test handling of invalid JSON."""
    from click.exceptions import Exit

    with (
        patch("builtins.open", mock_open(read_data="invalid json")),
        patch("pilot_metrics.main.console.print") as mock_print,
        pytest.raises(Exit),
    ):
        load_data("invalid.json")

        mock_print.assert_any_call(
            "[bold red]Error: Invalid JSON data provided.[/bold red]"
        )


def test_visualize_command():
    """Test the visualize command."""
    runner = CliRunner()

    sample_data = [
        {
            "date": "2024-01-15",
            "total_active_users": 100,
            "total_engaged_users": 80,
            "copilot_ide_code_completions": {
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
            "copilot_ide_chat": {"total_engaged_users": 30, "editors": []},
            "copilot_dotcom_chat": {"total_engaged_users": 20, "models": []},
            "copilot_dotcom_pull_requests": {
                "total_engaged_users": 15,
                "repositories": [],
            },
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_data, f)
        temp_file = f.name

    try:
        with patch("pilot_metrics.main.create_dashboard") as mock_viz:
            result = runner.invoke(app, ["visualize", temp_file])

            assert result.exit_code == 0
            assert "Successfully parsed 1 daily records" in result.stdout
            assert "Generating local dashboard" in result.stdout
            mock_viz.assert_called_once()
    finally:
        os.unlink(temp_file)


def test_upload_to_bq_command():
    """Test the upload-to-bq command."""
    runner = CliRunner()

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
            "copilot_ide_chat": {"total_engaged_users": 30, "editors": []},
            "copilot_dotcom_chat": {"total_engaged_users": 20, "models": []},
            "copilot_dotcom_pull_requests": {
                "total_engaged_users": 15,
                "repositories": [],
            },
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_data, f)
        temp_file = f.name

    try:
        with (
            patch("pilot_metrics.main.upload_to_bigquery") as mock_upload,
            patch.dict(
                "os.environ",
                {"GCP_PROJECT_ID": "test-project", "BQ_DATASET": "test-dataset"},
            ),
        ):
            result = runner.invoke(app, ["upload-to-bq", temp_file])

            assert result.exit_code == 0
            assert "Successfully parsed 1 daily records" in result.stdout
            assert "Starting upload to BigQuery" in result.stdout
            mock_upload.assert_called_once()
    finally:
        os.unlink(temp_file)


def test_help_command():
    """Test the help command."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "pilot-metrics" in result.stdout
    assert "visualize" in result.stdout
    assert "upload-to-bq" in result.stdout
