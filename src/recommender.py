import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

class ContentRecommender:
    def __init__(self, processed_data_path="data/processed_movies.csv"):
        self.processed_data_path = processed_data_path
        self.df = None
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self.vectorizer = None

    def load_and_build(self, model_path="models/content_model.pkl"):
        """Loads data and builds the TF-IDF similarity matrix."""
        if os.path.exists(model_path):
            print(f"Loading pre-trained model from {model_path}")
            model = joblib.load(model_path)
            self.df = model['df']
            self.tfidf_matrix = model['tfidf_matrix']
            self.similarity_matrix = model['similarity_matrix']
            self.vectorizer = model['vectorizer']
        else:
            print("Building content-based model...")
            self.df = pd.read_csv(self.processed_data_path)

            # TF-IDF on the combined features column
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])

            # Compute cosine similarity
            self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

            # Save the model
            model = {
                'df': self.df,
                'tfidf_matrix': self.tfidf_matrix,
                'similarity_matrix': self.similarity_matrix,
                'vectorizer': self.vectorizer
            }
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(model, model_path)
            print(f"Model saved to {model_path}")

    def get_similar_movies(self, movie_id, top_n=50):
        """Returns the top N most similar movies to a given movie_id."""
        # Ensure movie_id exists in the dataframe index (handling potential ID mismatches)
        idx_list = self.df[self.df['Movie_ID'] == movie_id].index.tolist()
        if not idx_list:
            return []

        idx = idx_list[0]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Remove the movie itself and get top N
        sim_scores = sim_scores[1:top_n+1]

        movie_indices = [i[0] for i in sim_scores]
        return self.df.iloc[movie_indices]

    def get_candidates_by_genre(self, preferred_genres, top_n=50):
        """Returns high-popularity movies that match the user's preferred genres."""
        if not preferred_genres:
            return self.df.sample(top_n) # Fallback to random samples

        # Filter movies that match any of the preferred genres
        mask = self.df['Movie_Genre'].apply(
            lambda x: any(genre.strip().lower() in x.lower() for genre in preferred_genres)
        )
        genre_movies = self.df[mask]

        # Sort by popularity to get high-quality candidates
        candidates = genre_movies.sort_values(by='Movie_Popularity', ascending=False).head(top_n)

        if len(candidates) < top_n:
            # Fill remaining spots with random movies if needed
            remaining = top_n - len(candidates)
            others = self.df[~mask].sample(remaining)
            candidates = pd.concat([candidates, others])

        return candidates

if __name__ == "__main__":
    # Simple test script
    # Note: requires processed_movies.csv to exist
    try:
        rec = ContentRecommender()
        rec.load_and_build()
        # Test with first movie
        first_id = rec.df['Movie_ID'].iloc[0]
        sim = rec.get_similar_movies(first_id, top_n=5)
        print(f"Movies similar to {rec.df['Movie_Title'].iloc[0]}:")
        print(sim[['Movie_Title', 'Movie_Genre']])
    except Exception as e:
        print(f"Error: {e}")
