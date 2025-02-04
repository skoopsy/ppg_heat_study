import os
import pandas as pd
import re
from config import DATA_DIR, CONDITIONS, SENSOR_TYPES

COLUMN_MAPPING = {
    # ACC
    "Phone timestamp": "phone_datetime",
    "sensor timestamp [ns]": "sensor_clock[ns]",
    "X [mg]": "acc_x[mg]",
    "Y [mg]": "acc_y[mg]",
    "Z [mg]": "acc_z[mg]",
    
    # PPG
    "channel 0": "ppg_ch0",
    "channel 1": "ppg_ch1",
    "channel 2": "ppg_ch2",
    "ambient": "ppg_amb",
    
    # HR
    "HR [bpm]": "heart_rate[bpm]"
}


def clean_col_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns using a predefined mapping and strip whitespaces."""

    df.columns = df.columns.str.strip()  # Remove spaces
    df.rename(columns=COLUMN_MAPPING, inplace=True)  # Rename columns

    return df


def load_data_for_participant(participant_dir: str) -> dict:
    """
     Loads and categorizes data for a given subject. 

    Args:
        participant_dir: str - directory of files

    Returns:
        dict([condition][sensor_type][sensor_df])        
    """
    data = {category: {key: pd.DataFrame() for key in SENSOR_TYPES.keys()} for category in CONDITIONS}

    for category in CONDITIONS:
        category_path = os.path.join(DATA_DIR, participant_dir, category)
        if not os.path.exists(category_path):
            print(f"Missing category: {category} for {participant_dir}")
            continue

        for filename in os.listdir(category_path):
            file_path = os.path.join(category_path, filename)

            # Debugging: Print the detected files
            print(f"Checking file: {filename} in {category}")

            df = pd.read_csv(file_path, delimiter=";", header="infer")
            df = clean_col_names(df)

            for key, pattern in SENSOR_TYPES.items():
                if re.search(pattern, filename):
                    print(f"File matched pattern {key}: {filename}")
                    data[category][key] = pd.concat([data[category][key], df], axis=0)

    return data


def load_all_participants() -> dict:
    """
    Loads data for all participants in the dataset.

    Returns:
        dict( subject_id{ condition{ sensor_type{ sensor_df{ pd.DataFrame}}}}])        

    """

    participants = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    all_data = {}
    for participant in participants:
        print(f"Loading data for: {participant}")
        all_data[participant] = load_data_for_participant(participant)
    
    return all_data
