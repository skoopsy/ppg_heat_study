import pickle
import os

class CheckpointManager:
    """
    Encapsulate checkpoint functionality using pickle
    """
    
    def __init__(self, filename: str):
        """
        Initialise with given filename

        Args:
            filename (str): Filename to use for saving/loading checkpoint
        """
        
        self.filename = filename

    def save(self, data):
        """
        Save data to checkpoint file with pickle

        Args:
            data: Object to be pickled
        """
        # mkdir if doesnt exist
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Save data
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)
        print(f"Checkpoint saved: {self.filename}")

    def load(self):
        """
        Load and return data from checkpoint file .pkl

        Returns:
            Unpickled data object
        """
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Checkpoint file {self.filename} not found.")
        with open(self.filename,"rb") as f:
            data = pickle.load(f)
        print(f"Checkpoint loaded: {self.filename}")

        return data

    def exists(self):
        """
        Check if the checkpoint file exists

        Returns:
            (bool) True if checkpoint exists, else False.
        """
        return os.path.exists(self.filename)

