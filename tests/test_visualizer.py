from unittest.mock import patch

from pilot_metrics.visualizer import create_dashboard


def test_create_dashboard_empty_data():
    """Test dashboard creation with empty data."""
    with patch("builtins.print") as mock_print:
        create_dashboard([], [], [])
        mock_print.assert_called_with("No completion data to visualize")


def test_create_dashboard_with_data():
    """Test dashboard creation with sample data."""
    sample_data = [
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "python",
            "total_engaged_users": 20,
            "total_code_acceptances": 100,
            "total_code_suggestions": 150,
            "total_code_lines_accepted": 200,
            "total_code_lines_suggested": 300,
        },
        {
            "date": "2024-01-16",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "javascript",
            "total_engaged_users": 15,
            "total_code_acceptances": 80,
            "total_code_suggestions": 120,
            "total_code_lines_accepted": 160,
            "total_code_lines_suggested": 240,
        },
    ]

    # Mock the plotly and webbrowser functions
    with (
        patch("pilot_metrics.visualizer.pyo.plot") as mock_plot,
        patch("pilot_metrics.visualizer.webbrowser.open") as mock_browser,
        patch("builtins.print") as mock_print,
    ):
        create_dashboard(sample_data, [], [])

        # Verify plotly plot was called
        mock_plot.assert_called_once()
        call_args = mock_plot.call_args
        assert call_args[1]["filename"] == "dashboard.html"
        assert call_args[1]["auto_open"] is False

        # Verify browser was opened
        mock_browser.assert_called_once()

        # Verify success message
        mock_print.assert_called_with("Dashboard opened in browser")


def test_create_dashboard_browser_error():
    """Test dashboard creation when browser opening fails."""
    sample_data = [
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "python",
            "total_engaged_users": 20,
            "total_code_acceptances": 100,
            "total_code_suggestions": 150,
            "total_code_lines_accepted": 200,
            "total_code_lines_suggested": 300,
        }
    ]

    # Mock plotly but make webbrowser fail
    with (
        patch("pilot_metrics.visualizer.pyo.plot") as mock_plot,
        patch(
            "pilot_metrics.visualizer.webbrowser.open",
            side_effect=Exception("Browser error"),
        ) as mock_browser,
        patch("builtins.print") as mock_print,
    ):
        create_dashboard(sample_data, [], [])

        # Verify plotly plot was still called
        mock_plot.assert_called_once()

        # Verify browser was attempted
        mock_browser.assert_called_once()

        # Verify error handling
        mock_print.assert_any_call(
            "Could not open browser automatically: Browser error"
        )
        mock_print.assert_any_call(
            "Please open 'dashboard.html' manually in your browser"
        )


def test_create_dashboard_file_path():
    """Test that absolute file path is used for browser opening."""
    sample_data = [
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "python",
            "total_engaged_users": 20,
            "total_code_acceptances": 100,
            "total_code_suggestions": 150,
            "total_code_lines_accepted": 200,
            "total_code_lines_suggested": 300,
        }
    ]

    with (
        patch("pilot_metrics.visualizer.pyo.plot"),
        patch("pilot_metrics.visualizer.webbrowser.open") as mock_browser,
        patch("pilot_metrics.visualizer.os.path.abspath") as mock_abspath,
    ):
        mock_abspath.return_value = "/full/path/to/dashboard.html"

        create_dashboard(sample_data, [], [])

        # Verify absolute path was used
        mock_abspath.assert_called_with("dashboard.html")
        mock_browser.assert_called_with("file:///full/path/to/dashboard.html")


def test_data_processing_in_dashboard():
    """Test that data is properly processed for visualization."""
    sample_data = [
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "python",
            "total_engaged_users": 20,
            "total_code_acceptances": 100,
            "total_code_suggestions": 150,
            "total_code_lines_accepted": 200,
            "total_code_lines_suggested": 300,
        },
        {
            "date": "2024-01-15",
            "editor": "vscode",
            "model": "gpt-4",
            "language": "javascript",
            "total_engaged_users": 15,
            "total_code_acceptances": 80,
            "total_code_suggestions": 120,
            "total_code_lines_accepted": 160,
            "total_code_lines_suggested": 240,
        },
    ]

    # Mock plotly to capture the figure
    with (
        patch("pilot_metrics.visualizer.pyo.plot") as mock_plot,
        patch("pilot_metrics.visualizer.webbrowser.open"),
        patch("builtins.print"),
    ):
        create_dashboard(sample_data, [], [])

        # Get the figure object passed to plot
        fig = mock_plot.call_args[0][0]

        # Verify figure has the expected structure
        assert fig.data  # Should have traces
        assert len(fig.data) >= 3  # At least stacked bars + line + other charts

        # Verify layout includes title with timeframe
        assert "GitHub Copilot Usage Dashboard" in fig.layout.title.text
        assert "Data from" in fig.layout.title.text
