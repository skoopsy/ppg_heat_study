import os

DATA_DIR = "data/"

# Regex patterns for different data types
SENSOR_TYPES= {
    "hr": r".*_HR\.txt",
    "acc": r".*_ACC\.txt",
    "ppg": r".*_PPG\.txt",
    "gyro": r".*_GYRO\.txt",
}

# Exposure categories
CONDITIONS = ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"]

# For checkpointing
LOAD_CHECKPOINT = True
SAVE_CHECKPOINT = False
CHECKPOINT_FILE = "data/pickled/ID00_loaded_data_000.pkl"
CHECKPOINT_ID = 0

# Function to get participant directories
def get_participant_dirs():
    return [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
