from src.rl_agent import ContextualBanditAgent
from src.user_profile import UserProfileManager

class FeedbackHandler:
    def __init__(self, rl_agent, user_manager):
        self.rl_agent = rl_agent
        self.user_manager = user_manager

    def map_rating_to_reward(self, rating):
        """
        Maps a 1-5 star rating to a reward value between -1.0 and 1.0.
        1 -> -1.0
        2 -> -0.5
        3 -> 0.0
        4 -> 0.5
        5 -> 1.0
        """
        reward_map = {
            1: -1.0,
            2: -0.5,
            3: 0.0,
            4: 0.5,
            5: 1.0
        }
        return reward_map.get(rating, 0.0)

    def process_feedback(self, user_id, movie_id, rating, movie_df):
        """
        Processes user feedback: updates user profile and RL agent.
        """
        # 1. Map rating to reward
        reward = self.map_rating_to_reward(rating)

        # 2. Update User Profile
        self.user_manager.update_history(user_id, movie_id, rating)

        # 3. Update RL Agent
        # Find the movie's genres
        movie_row = movie_df[movie_df['Movie_ID'] == movie_id]
        if not movie_row.empty:
            genres = str(movie_row['Movie_Genre'].values[0]).split(',')
            for genre in genres:
                self.rl_agent.update_q_value(genre, reward)

            # Decay epsilon to reduce exploration over time
            self.rl_agent.decay_epsilon()

        return reward

if __name__ == "__main__":
    # Mock RL Agent and User Manager
    from src.rl_agent import ContextualBanditAgent
    import pandas as pd

    genres = ["Action", "Comedy", "Drama"]
    rl = ContextualBanditAgent(genres)
    upm = UserProfileManager()
    fh = FeedbackHandler(rl, upm)

    # Mock movie df
    df = pd.DataFrame({
        'Movie_ID': [1],
        'Movie_Genre': ['Action,Comedy']
    })

    reward = fh.process_feedback("user1", 1, 5, df)
    print(f"Reward: {reward}")
    print(f"Updated Q-values: {rl.q_table}")
