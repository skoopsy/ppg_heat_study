from loader import load_all_participants
from preprocessor import merge_data, compute_sample_rate_for_sensor
from visualiser import visualise_data_availability, plot_data_coverage_per_participant, plot_individual_participant_heatmap, visualise_ppg_ch0_minutes_stacked
def main():
    all_data = load_all_participants()
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
