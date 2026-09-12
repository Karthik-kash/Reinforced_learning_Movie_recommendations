import numpy as np
import joblib
import os
import random

class ContextualBanditAgent:
    def __init__(self, genres_list, epsilon=0.2, alpha=0.1):
        """
        Reinforcement Learning Agent for personalized reranking.

        :param genres_list: List of all unique genres in the dataset.
        :param epsilon: Exploration rate for epsilon-greedy strategy.
        :param alpha: Learning rate for Q-value updates.
        """
        self.genres = genres_list
        self.epsilon = epsilon
        self.alpha = alpha
        # Q-table: Estimated reward for each genre
        # Initialize all Q-values to 0
        self.q_table = {genre: 0.0 for genre in genres_list}

    def get_reranked_list(self, candidates, user_profile):
        """
        Reranks candidates based on the RL agent's learned preferences.

        :param candidates: DataFrame of candidate movies.
        :param user_profile: Dictionary containing user preferences.
        :return: Reranked DataFrame and a list of reasons.
        """
        if candidates.empty:
            return candidates, []

        # Determine if we explore or exploit
        explore = random.random() < self.epsilon

        reranked_data = []
        reasons = []

        for idx, row in candidates.iterrows():
            movie_genres = str(row['Movie_Genre']).split(',')

            # Calculate combined Q-value for the movie's genres
            # We take the average Q-value of all genres the movie belongs to
            movie_q_values = [self.q_table.get(g.strip(), 0.0) for g in movie_genres]
            avg_q = np.mean(movie_q_values) if movie_q_values else 0.0

            # If exploring, we can give a random bonus to diverse movies
            if explore:
                # Exploration: randomly boost a movie
                score = random.random()
                reason = "Something new to try!"
            else:
                # Exploitation: Use the learned Q-value to boost the score
                # Final Score = Base Similarity (if provided) + RL Boost
                # Here we use avg_q as the boost.
                # We add 1.0 to ensure score stays positive for sorting if base is 0.
                score = 1.0 + avg_q

                # Explain why it was recommended
                best_genre = max(movie_genres, key=lambda g: self.q_table.get(g.strip(), 0.0))
                if self.q_table.get(best_genre.strip(), 0.0) > 0:
                    reason = f"Based on your love for {best_genre.strip()} movies"
                else:
                    reason = "Matches your general preferences"

            reranked_data.append((idx, score, reason))

        # Sort by score descending
        reranked_data.sort(key=lambda x: x[1], reverse=True)

        # Extract sorted indices and reasons
        sorted_indices = [item[0] for item in reranked_data]
        final_reasons = [item[2] for item in reranked_data]

        # Return the re-ordered candidates DataFrame
        return candidates.loc[sorted_indices], final_reasons

    def update_q_value(self, genre, reward):
        """
        Updates the expected reward for a genre using the incremental update rule:
        Q(g) = Q(g) + alpha * (Reward - Q(g))
        """
        genre = genre.strip()
        if genre in self.q_table:
            old_q = self.q_table[genre]
            self.q_table[genre] = old_q + self.alpha * (reward - old_q)
        else:
            # New genre encountered
            self.q_table[genre] = reward * self.alpha

    def decay_epsilon(self, decay_rate=0.995, min_epsilon=0.05):
        """Gradually reduce exploration as the agent learns."""
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)

    def save_model(self, path="models/rl_agent.pkl"):
        """Persists the RL agent's Q-table and parameters."""
        model_data = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'alpha': self.alpha,
            'genres': self.genres
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model_data, path)

    def load_model(self, path="models/rl_agent.pkl"):
        """Loads the RL agent's Q-table and parameters."""
        if os.path.exists(path):
            model_data = joblib.load(path)
            self.q_table = model_data['q_table']
            self.epsilon = model_data['epsilon']
            self.alpha = model_data['alpha']
            self.genres = model_data['genres']
            return True
        return False

if __name__ == "__main__":
    # Simple test script
    genres = ["Action", "Comedy", "Drama", "Sci-Fi"]
    agent = ContextualBanditAgent(genres)

    # Simulate feedback for Action movies
    print("Simulating positive feedback for Action...")
    for _ in range(5):
        agent.update_q_value("Action", 1.0) # 5 star rating

    print(f"Q-values: {agent.q_table}")

    # Mock candidates
    mock_df = pd.DataFrame({
        'Movie_ID': [1, 2, 3],
        'Movie_Title': ['Action Movie', 'Comedy Movie', 'Drama Movie'],
        'Movie_Genre': ['Action', 'Comedy', 'Drama']
    })

    reranked, reasons = agent.get_reranked_list(mock_df, {})
    print("\nReranked Movies:")
    print(reranked[['Movie_Title', 'Movie_Genre']])
    print("Reasons:", reasons)
