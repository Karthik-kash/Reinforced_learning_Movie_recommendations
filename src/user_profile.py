import json
import os
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class UserProfileManager:
    def __init__(self, storage_path="user_data/interactions.json"):
        self.storage_path = storage_path
        self.users = self._load_all_users()

    def _load_all_users(self):
        """Loads all user profiles from the JSON file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_all_users(self):
        """Persists all user profiles to the JSON file."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        def clean_numpy(obj):
            """Recursively convert numpy types to python types."""
            if isinstance(obj, dict):
                return {k: clean_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_numpy(i) for i in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return clean_numpy(obj.tolist())
            return obj

        cleaned_users = clean_numpy(self.users)
        with open(self.storage_path, 'w') as f:
            json.dump(cleaned_users, f, indent=4)

    def create_profile(self, user_id, preferred_genres=None):
        """Creates a new user profile."""
        self.users[user_id] = {
            'user_id': user_id,
            'preferred_genres': preferred_genres or [],
            'watched_movies': [], # List of Movie_IDs
            'rated_movies': {},    # {Movie_ID: rating}
            'watchlist': [],       # List of Movie_IDs
            'total_ratings': 0,
            'avg_rating': 0.0
        }
        self.save_all_users()
        return self.users[user_id]

    def get_profile(self, user_id):
        """Retrieves the profile for a specific user."""
        return self.users.get(user_id)

    def update_history(self, user_id, movie_id, rating=None):
        """Updates the user's interaction history."""
        movie_id = int(movie_id) # Ensure movie_id is a native Python int for JSON serialization
        if user_id not in self.users:
            self.create_profile(user_id)

        profile = self.users[user_id]

        # Mark as watched
        if movie_id not in profile['watched_movies']:
            profile['watched_movies'].append(movie_id)

        # Store rating if provided
        if rating is not None:
            profile['rated_movies'][str(movie_id)] = rating
            profile['total_ratings'] += 1
            # Update average rating
            ratings = list(profile['rated_movies'].values())
            profile['avg_rating'] = sum(ratings) / len(ratings)

        self.save_all_users()
        return profile

    def add_to_watchlist(self, user_id, movie_id):
        """Adds a movie to the user's watchlist."""
        movie_id = int(movie_id) # Ensure movie_id is a native Python int for JSON serialization
        if user_id not in self.users:
            self.create_profile(user_id)

        profile = self.users[user_id]
        if movie_id not in profile['watchlist']:
            profile['watchlist'].append(movie_id)
            self.save_all_users()

    def remove_from_watchlist(self, user_id, movie_id):
        """Removes a movie from the user's watchlist."""
        movie_id = int(movie_id) # Ensure movie_id is a native Python int
        if user_id in self.users:
            profile = self.users[user_id]
            if movie_id in profile['watchlist']:
                profile['watchlist'].remove(movie_id)
                self.save_all_users()

if __name__ == "__main__":
    # Simple test script
    upm = UserProfileManager()
    upm.create_profile("user123", ["Action", "Sci-Fi"])
    upm.update_history("user123", 101, 5)
    print(upm.get_profile("user123"))
