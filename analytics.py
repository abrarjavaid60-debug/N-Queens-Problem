"""Charts and summary metrics for the Smart Campus dashboard."""
import matplotlib.pyplot as plt
import pandas as pd


def make_category_chart(df):
    counts = df["category"].value_counts().sort_values(ascending=True) if not df.empty else pd.Series(dtype=int)
    fig, ax = plt.subplots(figsize=(8, 4))
    if counts.empty:
        ax.text(0.5, 0.5, "No complaints yet", ha="center", va="center")
        ax.set_axis_off()
    else:
        counts.plot(kind="barh", ax=ax)
        ax.set_xlabel("Number of complaints")
        ax.set_ylabel("Category")
        ax.set_title("Complaints by category")
        ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return fig


def make_status_chart(df):
    statuses = ["Pending", "In Progress", "Resolved"]
    counts = df["status"].value_counts().reindex(statuses, fill_value=0) if not df.empty else pd.Series([0, 0, 0], index=statuses)
    fig, ax = plt.subplots(figsize=(6, 4))
    if int(counts.sum()) == 0:
        ax.text(0.5, 0.5, "No complaints yet", ha="center", va="center")
        ax.set_axis_off()
    else:
        ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90)
        ax.set_title("Complaint resolution status")
    fig.tight_layout()
    return fig


