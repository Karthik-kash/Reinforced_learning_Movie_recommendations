import os
import joblib

def ensure_dir(path):
    """Ensures that the directory for a given path exists."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def load_pickle(path):
    """Loads a pickle file."""
    if os.path.exists(path):
        return joblib.load(path)
    return None

def save_pickle(obj, path):
    """Saves an object to a pickle file."""
    ensure_dir(path)
    joblib.dump(obj, path)
