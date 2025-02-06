import os

from config import LOAD_CHECKPOINT, SAVE_CHECKPOINT, CHECKPOINT_ID,  CHECKPOINT_FILE
from loader import load_all_participants
from checkpoint_manager import CheckpointManager
from preprocessor import merge_data, compute_sample_rate_for_sensor
from visualiser import visualise_data_availability, plot_data_coverage_per_participant, plot_individual_participant_heatmap, visualise_ppg_ch0_minutes_stacked

def main():

    checkpoint_mgr = CheckpointManager(CHECKPOINT_FILE)

    # Data loading
    if CHECKPOINT_ID == 0:
        if LOAD_CHECKPOINT and checkpoint_mgr.exists():
            # Load data from pickle file
            all_data = checkpoint_mgr.load()
        elif CHECKPOINT_ID == 0:
            # Load data from raw
            all_data = load_all_participants()
            if SAVE_CHECKPOINT:
                checkpoint_mgr.save(all_data)
    
    breakpoint()    
    merged_data = {
        participant: {cat: merge_data(all_data[participant], cat) for cat in all_data[participant]}
        for participant in all_data
    }
    breakpoint()     
    #visualise_data_availability(all_data)
    visualise_ppg_ch0_minutes_stacked(all_data)
    #visualise_ppg_minutes_data_availability(all_data)
    #plot_data_coverage_per_participant(all_data)
    #plot_individual_participant_heatmap(merged_data)

if __name__ == "__main__":
    main()
