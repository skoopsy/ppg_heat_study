import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

from preprocessor import compute_sample_rate_for_sensor 



def visualise_ppg_ch0_minutes_stacked(all_data: dict):
    """
    For each participant and each exposure category (pre/intra/post), accumulate
    all the *unique minutes* in which ppg_ch0 data is present. Then produce a stacked
    bar chart, so you can easily compare how many minutes are available per participant
    and how much of that belongs to each category.

    We specifically color the bars:
        pre_heat_exposure: 'darkblue'
        intra_heat_exposure: 'darkred'
        post_heat_exposure: 'darkgreen'
    """

    # Define the three categories we want to compare (in the order we want to plot them)
    categories = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]
    # Extract participant IDs (sorted for consistent order)
    participants = sorted(all_data.keys())

    # Define colors for each category
    category_colors = {
        "pre_heat_exposure": "darkblue",
        "intra_heat_exposure": "darkred",
        "post_heat_exposure": "darkgreen",
    }

    # Prepare a dictionary to store the count of unique minutes for each category
    cat_minutes_map = {cat: [] for cat in categories}

    for participant in participants:
        for cat in categories:
            # Safely get the 'ppg' DataFrame
            ppg_df = all_data[participant][cat].get("ppg", pd.DataFrame())

            # If there's no ppg data, or it's empty, store 0 minutes
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Focus specifically on ppg_ch0. Drop rows where ppg_ch0 is NaN
            if "ppg_ch0" not in ppg_df.columns:
                cat_minutes_map[cat].append(0)
                continue

            ppg_df = ppg_df.dropna(subset=["ppg_ch0"])
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Convert phone_datetime to a proper datetime, if not already
            ppg_df["phone_datetime"] = pd.to_datetime(ppg_df["phone_datetime"], errors="coerce")
            ppg_df = ppg_df.dropna(subset=["phone_datetime"])  # remove invalid timestamps
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Floor timestamps to the nearest minute
            ppg_df["minute"] = ppg_df["phone_datetime"].dt.floor("T")

            # Count how many unique minute values remain
            unique_minutes = ppg_df["minute"].nunique()
            cat_minutes_map[cat].append(unique_minutes)

    # Build a DataFrame where each row is a participant, each column is a category
    df_minutes = pd.DataFrame(cat_minutes_map, index=participants)

    # Stacked bar chart of unique minutes for each participant
    fig, ax = plt.subplots(figsize=(12, 6))

    # We'll manually stack the bars by tracking the 'bottom' as we plot each category
    bottom = np.zeros(len(df_minutes))

    for cat in categories:
        ax.bar(
            df_minutes.index,
            df_minutes[cat],
            bottom=bottom,
            color=category_colors[cat],
            label=cat
        )
        # Update the bottom for the next category in the stack
        bottom += df_minutes[cat].values

    ax.set_title("PPG Data Availability by Participant and Exposure Category", fontsize=14)
    ax.set_ylabel("Cumulative Minutes of ppg_ch0")
    ax.legend(title="Exposure Category")

    # Rotate participant labels if needed
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def visualise_ppg_ch0_minutes_stacked_old(all_data: dict):
    """
    For each participant and each exposure category (pre/intra/post), accumulate
    all the *unique minutes* in which ppg_ch0 data is present. Then produce a stacked
    bar chart, so you can easily compare how many minutes are available per participant
    and how much of that belongs to each category.

    Parameters
    ----------
    all_data : dict
        Dictionary of the form:
            all_data[participant][exposure_category]["ppg"] = DataFrame
        where 'ppg' has columns like:
            ['phone_datetime', 'sensor_clock[ns]', 'ppg_ch0', 'ppg_ch1', ...]
        The code specifically looks at 'ppg_ch0' to confirm data presence
        (by dropping rows with NaN in 'ppg_ch0').

    Produces
    --------
    A stacked bar chart (matplotlib) with:
      - x-axis: participant IDs
      - y-axis: total unique minutes of data (stacked by category)
      - legend: pre_heat_exposure, intra_heat_exposure, post_heat_exposure
    """

    # Define the three categories we want to compare
    categories = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]
    # Extract participant IDs
    participants = sorted(all_data.keys())

    # Prepare a dictionary to store the count of unique minutes for each category
    cat_minutes_map = {cat: [] for cat in categories}

    for participant in participants:
        # For each exposure category, find how many unique minutes have ppg_ch0 data
        for cat in categories:
            # Safely get the 'ppg' DataFrame
            ppg_df = all_data[participant][cat].get("ppg", pd.DataFrame())

            # If there's no ppg data, or it's empty, store 0 minutes
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Focus specifically on ppg_ch0. Drop rows where ppg_ch0 is NaN (no data)
            if "ppg_ch0" not in ppg_df.columns:
                cat_minutes_map[cat].append(0)
                continue

            ppg_df = ppg_df.dropna(subset=["ppg_ch0"])
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Convert phone_datetime to a proper datetime, if not already
            ppg_df["phone_datetime"] = pd.to_datetime(ppg_df["phone_datetime"], errors="coerce")
            ppg_df = ppg_df.dropna(subset=["phone_datetime"])  # remove invalid timestamps
            if ppg_df.empty:
                cat_minutes_map[cat].append(0)
                continue

            # Floor timestamps to the nearest minute
            ppg_df["minute"] = ppg_df["phone_datetime"].dt.floor("T")
            
            # Count how many unique minute values remain
            unique_minutes = ppg_df["minute"].nunique()
            cat_minutes_map[cat].append(unique_minutes)

    # Build a DataFrame where each row is a participant, each column is a category
    df_minutes = pd.DataFrame(cat_minutes_map, index=participants)

    # Stacked bar chart of unique minutes for each participant
    fig, ax = plt.subplots(figsize=(12, 6))

    # We'll manually stack the bars by tracking the 'bottom' as we plot each category
    bottom = np.zeros(len(df_minutes))
    # Use a Seaborn color palette (viridis) for consistency
    colors = sns.color_palette("viridis", n_colors=len(categories))

    for i, cat in enumerate(categories):
        ax.bar(
            df_minutes.index,
            df_minutes[cat],
            bottom=bottom,
            color=colors[i],
            label=cat
        )
        bottom += df_minutes[cat].values

    ax.set_title("PPG (ppg_ch0) Data Availability by Participant and Exposure Category", fontsize=14)
    ax.set_ylabel("Unique Minutes of ppg_ch0 Data")
    ax.legend(title="Exposure Category")

    # Rotate participant labels if needed
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def visualise_ppg_minutes_data_availability(data: dict):
    """
    Visualize estimated minutes of available PPG data for each participant and each exposure category,
    using computed sample rates for each session.
    """
    participants = list(data.keys())
    categories = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]

    # Compute sample rates for the PPG sensor group for all participants and categories.
    # This assumes that compute_sample_rate_for_sensor returns a DataFrame
    sample_rates_df = compute_sample_rate_for_sensor(data, sensor_group="ppg", sensor_name="ppg_ch0", time_col="sensor_clock[ns]", method="median")

    # Calculate estimated minutes per category using the computed sample rates.
    minutes_data = {}
    for cat in categories:
        minutes = []
        for p in participants:
            ppg_data = data[p][cat]["ppg_ch0"]
            if ppg_data.empty:
                minutes.append(0)
            else:
                sr = sample_rates_df.loc[p, cat]
                if sr is None or np.isnan(sr):
                    minutes.append(np.nan)
                else:
                    # Length of data divided by (sample rate * 60) to get minutes
                    minutes.append(len(ppg_data) / (sr * 60))
        minutes_data[cat] = minutes

    df = pd.DataFrame(minutes_data, index=participants)
    df.plot(kind="bar", stacked=True, figsize=(12, 6), colormap="viridis")
    plt.ylabel("Estimated Minutes of Data")
    plt.title("Estimated PPG Data Availability (in Minutes)")
    plt.legend(title="Exposure Category")
    plt.show()


def visualise_data_availability(data: dict):
    """ Creates a bar plot showing data availability for each participant. """
    participants = list(data.keys())
    categories = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]
    
    counts = {cat: [len(data[p][cat]["acc"]) for p in participants] for cat in categories}
    
    df = pd.DataFrame(counts, index=participants)
    
    df.plot(kind="bar", stacked=True, figsize=(12, 6), colormap="viridis")
    plt.ylabel("Number of Data Points")
    plt.title("Data Availability Across Participants")
    plt.legend(title="Exposure Category")
    plt.show()


def plot_data_coverage_per_participant(all_data: dict):
    """
    Plots the number of days each participant has data for,
    and within each day, the number of minutes of recorded data.
    """
    participant_days = []

    for participant, categories in all_data.items():
        for category, data_dict in categories.items():
            acc_data = data_dict["acc"]
            
            if acc_data.empty:
                continue  # Skip if no data

            # Convert timestamps to datetime
            acc_data["phone_datetime"] = pd.to_datetime(acc_data["phone_datetime"])
            acc_data["date"] = acc_data["phone_datetime"].dt.date  # Extract date only
            acc_data["time"] = acc_data["phone_datetime"].dt.floor("T")  # Round to minute

            # Count minutes per day
            daily_counts = acc_data.groupby("date")["time"].nunique()
            for day, minutes in daily_counts.items():
                participant_days.append({"participant": participant, "day": day, "minutes": minutes})

    # Convert to DataFrame
    df = pd.DataFrame(participant_days)

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="participant", y="minutes", hue="day", dodge=True)
    plt.xlabel("Participant")
    plt.ylabel("Minutes of Data Per Day")
    plt.title("Data Coverage Per Participant")
    plt.legend(title="Day of Recording", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.show()


def plot_individual_participant_heatmap(all_data: dict):
    """
    Generates a heatmap per participant showing time-of-day coverage across days.
    - Pre (Blue), Intra (Orange), Post (Green).
    - Time axis is binned into 10-minute intervals.
    - Only plots existing categories for each participant.
    - Layers each condition with a mask, alpha=1.0, vmin=0, vmax=1.
    - Title at the top of the Axes, legend horizontally below the x-axis labels.
    """
    
    # Colors for each condition
    category_colors = {
        "pre_heat_exposure": "Blues",
        "intra_heat_exposure": "Oranges",
        "post_heat_exposure": "Greens"
    }
    
    for participant, categories in all_data.items():
        # Collect presence data for each category
        presence_data_list = []
        category_labels = []
        
        for category, data_dict in categories.items():
            acc_data = data_dict["acc"]
            if acc_data.empty:
                continue  # No accelerometer data for this category

            # Convert timestamps
            acc_data["phone_datetime"] = pd.to_datetime(acc_data["phone_datetime"], errors="coerce")
            acc_data.dropna(subset=["phone_datetime"], inplace=True)
            acc_data["date"] = acc_data["phone_datetime"].dt.date
            
            # Bin into 10-minute chunks
            acc_data["time_bin"] = acc_data["phone_datetime"].dt.floor("10min").dt.strftime("%H:%M")

            # Mark presence (binary)
            presence = acc_data.groupby(["date", "time_bin"]).size().reset_index(name="count")
            presence["count"] = 1  # 1 = presence
            presence["category"] = category

            presence_data_list.append(presence)
            category_labels.append(category)

        # Skip if participant has no data in any category
        if not presence_data_list:
            print(f"No data available for {participant}")
            continue

        # Determine all unique dates
        all_dates = set()
        for df_presence in presence_data_list:
            all_dates.update(df_presence["date"].unique())
        all_dates = sorted(all_dates)

        if not all_dates:
            print(f"No valid dates for {participant}")
            continue

        full_time_range = pd.date_range("00:00", "23:59", freq="10min").strftime("%H:%M")
        full_grid = pd.DataFrame(
            [(d, tbin) for d in all_dates for tbin in full_time_range],
            columns=["date", "time_bin"]
        )

        for cat in category_labels:
            full_grid[cat] = 0

        # Merge presence data into full_grid
        for df_presence in presence_data_list:
            cat = df_presence["category"].iloc[0]
            merged = pd.merge(
                full_grid[["date", "time_bin", cat]],
                df_presence[["date", "time_bin", "count"]],
                on=["date", "time_bin"],
                how="left"
            ).fillna({"count": 0})
            
            merged[cat] = merged[cat] + merged["count"]
            merged.drop(columns=["count"], inplace=True)
            full_grid[cat] = merged[cat]

        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot each category with a mask
        for cat in category_labels:
            cat_data = full_grid.pivot(index="date", columns="time_bin", values=cat)
            if cat_data is None or cat_data.empty:
                continue

            cat_mask = (cat_data == 0)
            
            sns.heatmap(
                cat_data,
                cmap=category_colors[cat],
                linewidths=0.1,
                cbar=False,
                linecolor="white",
                mask=cat_mask,
                alpha=1.0,
                vmin=0,
                vmax=1,
                ax=ax
            )

        ax.set_title(f"Data Availability Heatmap for {participant}", fontsize=14)

        tick_positions = np.arange(0, len(full_time_range), 6)  # 6 x 10min = 1 hour
        tick_labels = pd.date_range("00:00", "23:59", freq="60min").strftime("%H:%M")
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=90)

        ax.set_xlabel("Time of Day (10-minute bins)")
        ax.set_ylabel("Date")

        # Build a horizontal legend for each category
        legend_patches = []
        for cat in category_labels:
            darkest_color = sns.color_palette(category_colors[cat], as_cmap=True)(1.0)
            legend_patches.append(
                mpatches.Patch(color=darkest_color, label=cat)
            )

        ax.legend(
            handles=legend_patches,
            title="Condition",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.2),  # Move below the Axes (negative y-offset)
            ncol=len(legend_patches),
            frameon=False
        )

        plt.subplots_adjust(bottom=0.3)  # Increase if legend is still clipped

        plt.show()
