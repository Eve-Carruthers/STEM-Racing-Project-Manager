"""
Scheduling utilities for the STEM Racing app.

This module contains helper functions to convert a list of tasks into a
pandas DataFrame and to plot an interactive Gantt chart using matplotlib.
While simplistic, it demonstrates how tasks can be visualised over time.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from .models import Task


def tasks_to_dataframe(tasks: Iterable[Task]) -> pd.DataFrame:
    """Convert tasks into a pandas DataFrame for schedule analysis.

    Columns include start, finish, duration, progress and role.
    """
    rows = []
    for t in tasks:
        rows.append(
            {
                "Task ID": t.id,
                "Task": t.name,
                "Start": t.start_date,
                "Finish": t.end_date,
                "Duration": t.duration(),
                "Progress": t.progress,
                "Role": str(t.assigned_role) if t.assigned_role else None,
            }
        )
    df = pd.DataFrame(rows)
    return df


def plot_gantt(tasks: Iterable[Task], title: str = "Project Schedule") -> None:
    """Plot a simple Gantt chart using matplotlib.

    Each task is plotted on its own horizontal line.  The chart
    automatically scales to the date range encompassed by all tasks.
    """
    df = tasks_to_dataframe(tasks)
    # Sort tasks by start date for clarity
    df = df.sort_values(by="Start")
    fig, ax = plt.subplots(figsize=(10, 0.5 * len(df) + 1))
    y_positions = range(len(df))
    # Convert dates to matplotlib date numbers
    start_dates = pd.to_datetime(df["Start"])
    end_dates = pd.to_datetime(df["Finish"])
    durations = (end_dates - start_dates).dt.days + 1
    ax.barh(y_positions, durations, left=start_dates.map(lambda d: d.toordinal()), height=0.4)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df["Task"])
    ax.set_xlabel("Date")
    ax.set_title(title)
    # Format x axis with date strings
    x_ticks = pd.date_range(start=start_dates.min(), end=end_dates.max(), freq="W")
    ax.set_xticks(x_ticks.map(lambda d: d.toordinal()))
    ax.set_xticklabels([d.strftime("%b %d") for d in x_ticks], rotation=45, ha="right")
    plt.tight_layout()
    plt.show()