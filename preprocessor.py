import pandas as pd
import numpy as np

def merge_data(data: dict, category: str) -> dict:
    """
    Merge accelerometer, PPG, HR, and gyro data on sensor clock timestamps.
    
    Returns:
        dict( subject_id{ condition{ pd.DataFrame}})
    """
    if category not in data:
        print(f"Warning: Category '{category}' is missing.")
        return pd.DataFrame()

    merged_df = None

    # Merge accelerometer
    if not data[category]["acc"].empty:
        acc_cols = ["sensor_clock[ns]", "phone_datetime", "acc_x[mg]", "acc_y[mg]", "acc_z[mg]"]
        if all(col in data[category]["acc"].columns for col in acc_cols):
            merged_df = data[category]["acc"][acc_cols].copy()

    # Debugging: Print column names for PPG
    if not data[category]["ppg"].empty:
        print(f"PPG Data Found for {category}: Columns -> {data[category]['ppg'].columns.tolist()}")

    # Merge PPG only if expected columns exist
    expected_ppg_cols = ["sensor_clock[ns]", "phone_datetime", "ppg_ch0", "ppg_ch1", "ppg_ch2", "ppg_amb"]
    if not data[category]["ppg"].empty and all(col in data[category]["ppg"].columns for col in expected_ppg_cols):
        merged_df = pd.merge(merged_df, data[category]["ppg"][expected_ppg_cols], on="sensor_clock[ns]", how="outer")
    else:
        print(f"Warning: PPG data in {category} does not have the expected columns!")

    return merged_df



def compute_sample_rate_from_timestamps_median(time_series):
    """
    Compute the sample rate (Hz) from a list of sensor clock timestamps (in nanoseconds)
    using the median difference between consecutive timestamps.
    
    Parameters:
        time_series (list or array-like): List of timestamps in nanoseconds.
    
    Returns:
        float or None: The computed sample rate in Hz, or None if insufficient data.
    """
    # Ensure time_series is a numpy array for proper sorting and diff.
    times = np.array(time_series)
    
    if times.size < 2:
        return None

    sorted_times = np.sort(times)
    # Compute differences between successive timestamps
    diffs = np.diff(sorted_times)
    median_diff_ns = np.median(diffs)
    if median_diff_ns == 0:
        return None
    # Convert median difference from nanoseconds to seconds and take reciprocal
    sample_rate = 1 / (median_diff_ns / 1e9)
    return sample_rate

def compute_sample_rate_for_sensor(data: dict, 
                                   sensor_group: str = "ppg",
                                   sensor_name: str = "ppg_ch0",
                                   time_col: str = "sensor_clock[ns]",
                                   method: str = "median"
):
    """
    Compute the sample rate (Hz) for a specified sensor (e.g. "ppg_ch0") for each participant
    and each exposure category based on the sensor clock timestamps.
    
    The function assumes that your data is structured as follows:
    
        data = {
            "participant1": {
                "pre_heat_exposure": {
                    sensor_group: {
                        "phone_datetime": [...],
                        "sensor_clock[ns]": [...],
                        "ppg_ch0": [...],
                        ... (other sensor channels)
                    },
                    ... (possibly other sensor groups)
                },
                "intra_heat_exposure": { ... },
                "post_heat_exposure": { ... },
            },
            "participant2": { ... },
            ...
        }
    
    Parameters:
        data (dict): The nested data dictionary.
        sensor_group (str): The key for the sensor group (e.g. "ppg") where the timestamps are stored.
        sensor_name (str): The key for the sensor data (e.g., "ppg_ch0").
                           (Note: In this function the sample rate is computed from the time stamps in time_col.)
        time_col (str): The key in the sensor group that contains the timestamps (default "sensor_clock[ns]").
        method (str): Which method to use for computing the sample rate. Options:
                      "median" for the median-difference method,
                      "total" for the total-duration method (not implemented here).
    
    Returns:
        pd.DataFrame: A DataFrame indexed by participants with columns for each exposure category containing
                      the computed sample rate in Hz.
    """
    participants = list(data.keys())
    categories = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]
    
    sample_rate_data = {}
    for cat in categories:
        rates = []
        for p in participants:
            if cat not in data[p]:
                print(f"Warning: Category '{cat}' not found for participant '{p}'.")
                rates.append(np.nan)
                continue
            
            # Check if the sensor_group exists in the category.
            if sensor_group not in data[p][cat]:
                print(f"Warning: Sensor group '{sensor_group}' not found for participant '{p}', category '{cat}'.")
                rates.append(np.nan)
                continue
            
            # Extract the time stamps from the specified time_col within the sensor group.
            time_series = data[p][cat][sensor_group].get(time_col, [])
            # Handle the possibility that time_series is a pandas Series.
            if isinstance(time_series, pd.Series):
                if time_series.empty:
                    print(f"Warning: Timestamp Series for '{time_col}' is empty for participant '{p}', category '{cat}'.")
                    rates.append(np.nan)
                    continue
                # Convert to a list (or numpy array) for further processing.
                time_series = time_series.tolist()
            else:
                if not isinstance(time_series, list) and not hasattr(time_series, '__len__'):
                    print(f"Warning: Timestamp data for '{time_col}' for participant '{p}', category '{cat}' is not list-like.")
                    rates.append(np.nan)
                    continue
                if len(time_series) == 0:
                    print(f"Warning: No timestamp data found in '{time_col}' for participant '{p}', category '{cat}'.")
                    rates.append(np.nan)
                    continue
            
            # Compute the sample rate using the selected method.
            if method == "median":
                rate = compute_sample_rate_from_timestamps_median(time_series)
            else:
                raise ValueError("Method not implemented. Please use method='median'.")
            
            rates.append(rate)
        sample_rate_data[cat] = rates
    
    df_rates = pd.DataFrame(sample_rate_data, index=participants)
    return df_rates



def compute_file_level_sample_rates(data: dict,
                                    sensor_group: str = "ppg",
                                    time_col: str = "sensor_clock[ns]"
):
    """
    Computes the sample rate for each file for a given sensor group.
    This function assumes that in your loader you stored a list of DataFrames per sensor type per category.
    Returns a nested dictionary structured as:
        { participant: { category: [sample_rate_file1, sample_rate_file2, ...] } }
    """
    sample_rates = {}
    for participant in data:
        sample_rates[participant] = {}
        for category in data[participant]:
            # Suppose data[participant][category][sensor_group] is now a list of DataFrames
            file_rates = []
            for df in data[participant][category][sensor_group]:
                if df.empty or time_col not in df.columns or len(df[time_col]) < 2:
                    file_rates.append(np.nan)
                else:
                    rate = compute_sample_rate_from_timestamps_median(df[time_col].tolist())
                    file_rates.append(rate)
            sample_rates[participant][category] = file_rates
    return sample_rates
