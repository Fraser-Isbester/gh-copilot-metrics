import json
import sys
from typing import Annotated

import typer
from rich.console import Console

from .bigquery_uploader import upload_to_bigquery
from .models import CopilotData
from .processing import flatten_copilot_data
from .visualizer import create_dashboard

app = typer.Typer(
    name="pilot-metrics",
    help="CLI to process and visualize GitHub Copilot usage data.",
    add_completion=False,
)
console = Console()


def load_data(input_file: str) -> list:
    """Load and parse Copilot data from file or stdin."""
    if input_file == "-":
        console.print("[cyan]Reading data from stdin...[/cyan]")
        try:
            raw_data = json.load(sys.stdin)
        except (json.JSONDecodeError, TypeError):
            console.print("[bold red]Error: Invalid JSON data provided.[/bold red]")
            raise typer.Exit(code=1) from None
    else:
        console.print(f"[cyan]Reading data from '{input_file}'...[/cyan]")
        try:
            with open(input_file) as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            console.print(f"[bold red]Error: File '{input_file}' not found.[/bold red]")
            raise typer.Exit(code=1) from None
        except (json.JSONDecodeError, TypeError):
            console.print("[bold red]Error: Invalid JSON data provided.[/bold red]")
            raise typer.Exit(code=1) from None

    try:
        parsed_data = CopilotData.model_validate(raw_data)
        console.print(
            f"[green]Successfully parsed {len(parsed_data.root)} daily records.[/green]"
        )
        return parsed_data.root
    except Exception as e:
        console.print(
            f"[bold red]An unexpected error occurred during parsing: {e}[/bold red]"
        )
        raise typer.Exit(code=1) from None


@app.command()
def upload_to_bq(
    input_file: Annotated[
        str,
        typer.Argument(
            help="Path to the JSON data file. Use '-' to read from stdin.",
        ),
    ] = "-",
):
    """
    Uploads the processed data to BigQuery tables.
    Requires GCP_PROJECT_ID and BQ_DATASET env variables.
    """
    daily_stats = load_data(input_file)
    completions, chats, pr_data = flatten_copilot_data(daily_stats)

    console.print("[cyan]Starting upload to BigQuery...[/cyan]")
    try:
        upload_to_bigquery(completions, chats)
        console.print("[bold green]BigQuery upload complete.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]BigQuery upload failed: {e}[/bold red]")
        raise typer.Exit(code=1) from None


@app.command()
def visualize(
    input_file: Annotated[
        str,
        typer.Argument(
            help="Path to the JSON data file. Use '-' to read from stdin.",
        ),
    ] = "-",
):
    """
    Generates a local, interactive HTML dashboard from the data.
    """
    daily_stats = load_data(input_file)
    completions, chats, pr_data = flatten_copilot_data(daily_stats)

    if not completions:
        console.print("[yellow]No completion data found to visualize.[/yellow]")
        raise typer.Exit()

    console.print("[cyan]Generating local dashboard...[/cyan]")
    create_dashboard(completions, chats, pr_data)
