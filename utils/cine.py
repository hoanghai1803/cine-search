from typing import List, Tuple
from .bm25 import BM25
from .tokenizer import Tokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Cine:

    def __init__(self, collection):
        """
        Cine class for searching movies.
        :param collection:
        """

        self.movies_id = []
        for document in collection.find():
            self.movies_id.append(document.get('movie_id', ''))

        self.titles = []
        for document in collection.find():
            self.titles.append(document.get('movie_name', ''))
        self.bm25_titles = BM25(self.titles)

        self.descriptions = []
        for document in collection.find():
            self.descriptions.append(document.get('movie_description', ''))
        self.bm25_descriptions = BM25(self.descriptions)

        # Get all terms in the collection
        title_terms = self.bm25_titles.terms
        description_terms = self.bm25_descriptions.terms
        self.terms = title_terms.union(description_terms)

        self.tokenizer = Tokenizer()

    def _extend_terms(
            self,
            query: str,
            num_extend_terms: int = 5
    ) -> str:
        """
        Extend the query with relative terms from the collection, based on cosine similarity.
        :param query:
        :param num_extend_terms:
        :return:
        """
        assert isinstance(query, str), "Query must be a string."
        assert isinstance(num_extend_terms, int), "num_extend_terms must be an integer."
        assert num_extend_terms > 0, "num_extend_terms must be a positive integer."

        query_terms = self.tokenizer.tokenize_text(query)
        collection_terms = list(self.terms)

        for query_term in query_terms:
            for collection_term in collection_terms:
                try:
                    vectorized = CountVectorizer().fit_transform([query_term, collection_term])
                    vectors = vectorized.toarray()
                    similarity = cosine_similarity(vectors)
                    if similarity[0][1] > 0.5:
                        collection_terms.remove(collection_term)
                except:
                    pass

        extended_terms = collection_terms[:num_extend_terms]
        new_query = ' '.join(query_terms + extended_terms)
        return new_query

    def _search(
            self,
            query: str,
    ):
        """
        Search for movies based on a query.
        :param query:
        :return: sorted list of tuples (movie_id, score)
        """

        assert isinstance(query, str), "Query must be a string."

        title_scores = self.bm25_titles.get_scores(query)
        description_scores = self.bm25_descriptions.get_scores(query)
        scores = [title_scores[i] + description_scores[i] for i in range(len(title_scores))]

        results = list(zip(self.movies_id, scores))
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def _bonus_score_for_contiguous_tokens(self, top_movies, query):
        tokens = self.tokenizer.tokenize_text(query)
        score_increase_factor = 0.75
        new_top_movies = []
        for movie_id, score in top_movies:
            movie_title = self.titles[self.movies_id.index(movie_id)]
            normalized_movie_title = ' '.join(self.tokenizer.tokenize_text(movie_title))
            for length in range(2, len(tokens) + 1):
                for i in range(len(tokens) - length + 1):
                    contiguous_tokens = ' '.join(tokens[i:i + length])
                    if contiguous_tokens in normalized_movie_title:
                        score += length * score_increase_factor * 3

            movie_description = self.descriptions[self.movies_id.index(movie_id)]
            normalized_movie_description = ' '.join(self.tokenizer.tokenize_text(movie_description))
            for length in range(2, len(tokens) + 1):
                for i in range(len(tokens) - length + 1):
                    contiguous_tokens = ' '.join(tokens[i:i + length])
                    if contiguous_tokens in normalized_movie_description:
                        score += length * score_increase_factor

            new_top_movies.append((movie_id, score))

        # Sort the top movies by score
        new_top_movies.sort(key=lambda x: x[1], reverse=True)
        return new_top_movies

    def cine_search(
        self,
        query: str,
        top_n: int = 20,
        num_extend_terms: int = 5
    ) -> List[int]:
        assert isinstance(query, str), "Query must be a string."
        assert isinstance(top_n, int), "top_n must be an integer."
        assert top_n > 0, "n must be a positive integer."

        results = self._search(query)

        top_movies = []
        for idx, result in enumerate(results):
            if idx == top_n or result[1] == 0:
                break
            top_movies.append(result)

        top_movies = self._bonus_score_for_contiguous_tokens(top_movies, query)

        # Extend the query and search again if the top_n movies are not found enough
        if len(top_movies) < top_n:
            new_query = self._extend_terms(query, num_extend_terms)
            results = self._search(new_query)
            for result in results:
                exists = any(result[0] == idx for idx, _ in top_movies)
                if not exists:
                    top_movies.append(result)
                if len(top_movies) == top_n:
                    break

        # Get the indices of the top movies
        result_movie_ids = [movie_id for movie_id, _ in top_movies]
        return result_movie_ids
