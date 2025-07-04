import os
import webbrowser
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots


def create_dashboard(
    completions_data: list[dict[str, Any]],
    chats_data: list[dict[str, Any]],
    pr_data: list[dict[str, Any]],
) -> None:
    """
    Creates an interactive HTML dashboard from flattened Copilot data.
    Saves as 'dashboard.html' and opens in browser.
    """
    if not completions_data:
        print("No completion data to visualize")
        return

    df = pd.DataFrame(completions_data)
    chats_df = pd.DataFrame(chats_data) if chats_data else pd.DataFrame()
    pr_df = pd.DataFrame(pr_data) if pr_data else pd.DataFrame()
    df["date"] = pd.to_datetime(df["date"])

    # Calculate timeframe for title
    start_date = df["date"].min().strftime("%Y-%m-%d")
    end_date = df["date"].max().strftime("%Y-%m-%d")
    timeframe = f"Data from {start_date} to {end_date}"

    # Create subplots
    fig = make_subplots(
        rows=4,
        cols=2,
        specs=[
            [{"colspan": 2}, None],  # Full width chart
            [{"secondary_y": True}, {"type": "pie"}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
        ],
    )

    # 1. Accumulated Lines of Code Over Time (Full Width) - Stacked by Language
    daily_language_totals = (
        df.groupby(["date", "language"])["total_code_lines_accepted"]
        .sum()
        .reset_index()
        .pivot(index="date", columns="language", values="total_code_lines_accepted")
        .fillna(0)
    )

    # Calculate cumulative sum for each language
    cumulative_language_totals = daily_language_totals.cumsum()

    # Add traces for each language
    for language in cumulative_language_totals.columns:
        fig.add_trace(
            go.Bar(
                x=cumulative_language_totals.index,
                y=cumulative_language_totals[language],
                name=f"{language}",
                legendgroup="group1",
                hovertemplate=f"<b>{language}</b><br>"
                + "Date: %{x}<br>"
                + "Lines: %{y:,}<br>"
                + "<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # 2. Code Acceptances by Language Over Time (Stacked Bar Chart)
    language_pivot = (
        df.groupby(["date", "language"])["total_code_acceptances"]
        .sum()
        .reset_index()
        .pivot(index="date", columns="language", values="total_code_acceptances")
        .fillna(0)
    )

    for language in language_pivot.columns:
        fig.add_trace(
            go.Bar(
                x=language_pivot.index,
                y=language_pivot[language],
                name=f"{language}",
                legendgroup="group1",
                hovertemplate="<b>%{fullData.name}</b><br>"
                + "Date: %{x}<br>"
                + "Acceptances: %{y}<br>"
                + "<extra></extra>",
            ),
            row=2,
            col=1,
        )

    # Add line chart overlay for total lines accepted
    lines_over_time = (
        df.groupby("date")["total_code_lines_accepted"].sum().reset_index()
    )

    fig.add_trace(
        go.Scatter(
            x=lines_over_time["date"],
            y=lines_over_time["total_code_lines_accepted"],
            mode="lines",
            name="Total Lines Accepted",
            line={"color": "red", "width": 1, "dash": "dot"},
            legendgroup="group1_lines",
            hovertemplate="<b>Total Lines Accepted</b><br>"
            + "Date: %{x}<br>"
            + "Lines: %{y}<br>"
            + "<extra></extra>",
            yaxis="y2",
        ),
        row=2,
        col=1,
        secondary_y=True,
    )

    # 3. Accepted Lines of Code by Editor (Pie Chart)
    editor_accepted_lines = (
        df.groupby("editor")["total_code_lines_accepted"].sum().reset_index()
    )

    fig.add_trace(
        go.Pie(
            labels=editor_accepted_lines["editor"],
            values=editor_accepted_lines["total_code_lines_accepted"],
            name="Accepted Lines",
            hovertemplate="<b>%{label}</b><br>"
            + "Lines: %{value}<br>"
            + "Percentage: %{percent}<br>"
            + "<extra></extra>",
        ),
        row=2,
        col=2,
    )

    # 4. Unique Active Users Per Day
    # Get unique active users per day from the original daily stats
    daily_users = []
    for daily_stat in df.groupby("date"):
        date = daily_stat[0]
        # Sum total_engaged_users across all editors for this date
        total_users = daily_stat[1][
            "total_engaged_users"
        ].max()  # Should be same across all rows for a date
        daily_users.append({"date": date, "active_users": total_users})

    daily_users_df = pd.DataFrame(daily_users)

    fig.add_trace(
        go.Bar(
            x=daily_users_df["date"],
            y=daily_users_df["active_users"],
            name="Active Users",
            legendgroup="group3",
            hovertemplate="<b>Active Users</b><br>"
            + "Date: %{x}<br>"
            + "Users: %{y}<br>"
            + "<extra></extra>",
        ),
        row=3,
        col=1,
    )

    # 5. Acceptance Rate by Language
    language_rates = (
        df.groupby("language")
        .agg({"total_code_suggestions": "sum", "total_code_acceptances": "sum"})
        .reset_index()
    )
    language_rates["acceptance_rate"] = (
        language_rates["total_code_acceptances"]
        / language_rates["total_code_suggestions"]
        * 100
    ).fillna(0)

    fig.add_trace(
        go.Bar(
            x=language_rates["language"],
            y=language_rates["acceptance_rate"],
            name="Acceptance Rate (%)",
            legendgroup="group4",
            hovertemplate="<b>%{x}</b><br>"
            + "Acceptance Rate: %{y:.1f}%<br>"
            + "<extra></extra>",
        ),
        row=3,
        col=2,
    )

    # 6. PR Summaries by Repository
    if not pr_df.empty:
        repo_summaries = (
            pr_df.groupby("repository")["total_pr_summaries_created"]
            .sum()
            .reset_index()
        )
        fig.add_trace(
            go.Bar(
                x=repo_summaries["repository"],
                y=repo_summaries["total_pr_summaries_created"],
                name="PR Summaries",
                legendgroup="group5",
                hovertemplate="<b>%{x}</b><br>"
                + "PR Summaries: %{y}<br>"
                + "<extra></extra>",
            ),
            row=4,
            col=1,
        )
    else:
        # Add empty placeholder if no PR data
        fig.add_trace(
            go.Bar(x=[], y=[], name="No PR Data", showlegend=False),
            row=4,
            col=1,
        )

    # 7. Chat Usage (Chats/Copies/Inserts)
    if not chats_df.empty:
        # Aggregate all chat data (total across all editors/types)
        total_chats = chats_df["total_chats"].sum()
        total_copies = chats_df["total_chat_copy_events"].sum()
        total_inserts = chats_df["total_chat_insertion_events"].sum()

        # Create simple bar chart
        categories = ["Total Chats", "Copies", "Inserts"]
        values = [total_chats, total_copies, total_inserts]
        colors = ["lightblue", "orange", "green"]

        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                name="Chat Usage",
                marker_color=colors,
                legendgroup="group6",
                hovertemplate="<b>%{x}</b><br>" + "Count: %{y}<br>" + "<extra></extra>",
            ),
            row=4,
            col=2,
        )
    else:
        # Add empty placeholder if no chat data
        fig.add_trace(
            go.Bar(x=[], y=[], name="No Chat Data", showlegend=False),
            row=4,
            col=2,
        )

    # Add subplot titles manually
    fig.add_annotation(
        text="Accumulated Lines of Code Over Time",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.98,
        showarrow=False,
        font={"size": 16},
        xanchor="center",
    )
    fig.add_annotation(
        text="Code Acceptances by Language Over Time",
        xref="paper",
        yref="paper",
        x=0.225,
        y=0.76,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )
    fig.add_annotation(
        text="Accepted Lines of Code by Editor",
        xref="paper",
        yref="paper",
        x=0.775,
        y=0.76,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )
    fig.add_annotation(
        text="Unique Active Users Per Day",
        xref="paper",
        yref="paper",
        x=0.225,
        y=0.52,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )
    fig.add_annotation(
        text="Acceptance Rate by Language",
        xref="paper",
        yref="paper",
        x=0.775,
        y=0.52,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )
    fig.add_annotation(
        text="PR Summaries by Repository",
        xref="paper",
        yref="paper",
        x=0.225,
        y=0.28,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )
    fig.add_annotation(
        text="Chat Usage (Chats/Copies/Inserts)",
        xref="paper",
        yref="paper",
        x=0.775,
        y=0.28,
        showarrow=False,
        font={"size": 14},
        xanchor="center",
    )

    # Update layout
    fig.update_layout(
        height=1400,  # Increased height for 4 rows
        title_text=f"GitHub Copilot Usage Dashboard<br><sub>{timeframe}</sub>",
        title_x=0.5,
        showlegend=True,
        barmode="stack",  # Make bars stack
    )

    # Update axes labels
    # Row 1 - Accumulated Lines (full width)
    fig.update_xaxes(
        title_text="Date",
        row=1,
        col=1,
        tickformat="%m/%d",
        tickangle=45,
    )
    fig.update_yaxes(title_text="Accumulated Lines of Code", row=1, col=1)

    # Row 2 - Code acceptances and pie chart
    fig.update_xaxes(
        title_text="Date",
        row=2,
        col=1,
        tickformat="%m/%d",  # Show as MM/DD format
        tickangle=45,  # Rotate labels for better readability
    )
    fig.update_yaxes(title_text="Code Acceptances", row=2, col=1)
    fig.update_yaxes(title_text="Lines of Code", row=2, col=1, secondary_y=True)

    # Note: Pie chart doesn't need axis labels

    # Row 3 - Active users and acceptance rate
    fig.update_xaxes(
        title_text="Date",
        row=3,
        col=1,
        tickformat="%m/%d",  # Show as MM/DD format
        tickangle=45,  # Rotate labels for better readability
    )
    fig.update_yaxes(title_text="Active Users", row=3, col=1)

    fig.update_xaxes(title_text="Language", row=3, col=2)
    fig.update_yaxes(title_text="Acceptance Rate (%)", row=3, col=2)

    # Row 4 - PR summaries and chat usage
    fig.update_xaxes(title_text="Repository", row=4, col=1)
    fig.update_yaxes(title_text="PR Summaries Created", row=4, col=1)

    fig.update_xaxes(title_text="Chat Metrics", row=4, col=2)
    fig.update_yaxes(title_text="Count", row=4, col=2)

    # Save and open dashboard
    output_file = "dashboard.html"
    pyo.plot(fig, filename=output_file, auto_open=False)

    print(f"Dashboard saved as '{output_file}'")

    # Open in browser
    try:
        # Get absolute path for file:// URL
        abs_path = os.path.abspath(output_file)
        webbrowser.open(f"file://{abs_path}")
        print("Dashboard opened in browser")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please open '{output_file}' manually in your browser")
