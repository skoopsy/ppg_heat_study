import pytest
from loader import load_data_for_participant

def test_load_data_for_participant():
    participant = "sample_participant"
    data = load_data_for_participant(participant)
    
    assert isinstance(data, dict)
    assert all(key in data for key in ["pre_heat_exposure", "intra_heat_exposure", "post_heat_exposure"])
