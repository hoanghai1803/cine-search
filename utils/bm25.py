import math
from .tokenizer import Tokenizer


class BM25:

    def __init__(
            self,
            corpus,
            k: float = 1.2,
            b: float = 0.75
    ):
        """
        BM25 class for scoring documents based on a query.
        :param corpus: List of documents.
        :param k: BM25 constant.
        :param b: BM25 constant.
        """

        self.corpus = corpus

        self.tokenizer = Tokenizer()
        self.tokenized_corpus = []
        for document in corpus:
            self.tokenized_corpus.append(self.tokenizer.tokenize_text(document))

        self.avg_doc_len = sum(len(doc) for doc in corpus) / len(corpus)
        self.k = k
        self.b = b
        self.idf = {}
        self.doc_len = [len(doc) for doc in corpus]
        self.corpus_size = len(corpus)
        self._initialize()

        # Get all terms in corpus
        self.terms = set()
        for document in self.tokenized_corpus:
            for word in document:
                self.terms.add(word)

    def _initialize(self):
        """
        Initialize IDF dictionary.
        :return:
        """
        for document in self.tokenized_corpus:
            for word in set(document):
                self.idf[word] = self.idf.get(word, 0) + 1

        for word, df in self.idf.items():
            self.idf[word] = math.log(1 + (self.corpus_size - df + 0.5) / (df + 0.5))

    def get_scores(self, query):
        """
        Get BM25 scores for documents in the corpus.
        :param query:
        :return:
        """

        query_terms = self.tokenizer.tokenize_text(query)
        scores = [0] * self.corpus_size
        doc_idx = 0
        for document in self.tokenized_corpus:
            score = 0
            doc_len = self.doc_len[doc_idx]
            for word in query_terms:
                if word not in self.idf:
                    continue
                f = document.count(word)
                score += self.idf[word] * (f * (self.k + 1)) / (
                            f + self.k * (1 - self.b + self.b * (doc_len / self.avg_doc_len)))
            scores[doc_idx] = score
            doc_idx += 1
        return scores
