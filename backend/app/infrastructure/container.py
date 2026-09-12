from dataclasses import dataclass

import pandas as pd

from src.data_preprocessing import MovieDataProcessor
from src.feedback import FeedbackHandler
from src.recommender import ContentRecommender
from src.rl_agent import ContextualBanditAgent
from src.user_profile import UserProfileManager

from backend.app.core.config import (
    CONTENT_MODEL_PATH,
    INTERACTIONS_PATH,
    MOVIES_PATH,
    POSTER_METADATA_PATH,
    PROCESSED_MOVIES_PATH,
    RL_MODEL_PATH,
)


@dataclass
class AppContainer:
    dataframe: object
    recommender: ContentRecommender
    rl_agent: ContextualBanditAgent
    profiles: UserProfileManager
    feedback: FeedbackHandler


def build_container() -> AppContainer:
    processor = MovieDataProcessor()
    dataframe = processor.load_data(save_path=str(MOVIES_PATH))
    dataframe = processor.create_combined_features()
    processor.save_processed_data(path=str(PROCESSED_MOVIES_PATH))
    dataframe["Movie_ID"] = dataframe["Movie_ID"].astype(int)

    recommender = ContentRecommender(processed_data_path=str(PROCESSED_MOVIES_PATH))
    recommender.load_and_build(model_path=str(CONTENT_MODEL_PATH))

    if POSTER_METADATA_PATH.exists():
        poster_metadata = pd.read_csv(POSTER_METADATA_PATH)
        poster_metadata = poster_metadata.drop_duplicates("Movie_ID")
        poster_columns = [column for column in ["Movie_ID", "tmdb_id", "poster_url", "backdrop_url"] if column in poster_metadata]
        poster_metadata = poster_metadata[poster_columns]
        dataframe = dataframe.merge(poster_metadata, on="Movie_ID", how="left")
        recommender.df = recommender.df.merge(poster_metadata, on="Movie_ID", how="left")

    genres = sorted(
        {
            genre.strip()
            for values in dataframe["Movie_Genre"].fillna("").str.split(",")
            for genre in values
            if genre.strip()
        }
    )
    rl_agent = ContextualBanditAgent(genres)
    rl_agent.load_model(path=str(RL_MODEL_PATH))

    profiles = UserProfileManager(storage_path=str(INTERACTIONS_PATH))
    feedback = FeedbackHandler(rl_agent, profiles)
    return AppContainer(dataframe, recommender, rl_agent, profiles, feedback)
