import string
from typing import List, Union, Set
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


class Tokenizer:

    def __init__(
            self,
            stop_words: Union[List[str], Set[str]] = None
    ):
        """
        Tokenizer class for normalizing text.
        :param stop_words:
        """
        if stop_words is None:
            self.stop_words = set(stopwords.words('english'))
        else:
            assert isinstance(stop_words, (list, set)), "Stop words must be a list or set."
            self.stop_words = set(stop_words)

    def _lowercase_text(self, text):
        """
        Convert the text to lowercase.

        Parameters:
        text (str): Input text.

        Returns:
        str: Text with all characters converted to lowercase.
        """
        return text.lower()

    def _remove_stop_words(self, text):
        """
        Remove specified stop words from the text.

        Parameters:
        text (str): Input text.

        Returns:
        str: Text with specified stop words removed.
        """
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)

    def _remove_punctuation(self, text):
        """
        Remove punctuation from the text.

        Parameters:
        text (str): Input text.

        Returns:
        str: Text with punctuation removed.
        """
        return text.translate(str.maketrans('', '', string.punctuation))

    def _stem_text(self, text):
        """
        Stem words in the text using the Porter stemmer algorithm.

        Parameters:
        text (str): Input text.

        Returns:
        str: Text with words stemmed.
        """
        ps = PorterStemmer()
        words = word_tokenize(text)
        stemmed_words = [ps.stem(word) for word in words]
        return stemmed_words

    def tokenize_text(self, text: str):
        """
        Normalize the text by applying lowercasing, tokenization, stop word removal, and stemming.

        Parameters:
        text (str): Input text.
        stop_words (list): List of stop words to be removed.

        Returns:
        str: Normalized text.
        """

        assert isinstance(text, str), "Input text must be a string."

        lowercased_text = self._lowercase_text(text)
        normalized_text = self._remove_punctuation(self._remove_stop_words(lowercased_text))
        tokenized_text = self._stem_text(normalized_text)
        return tokenized_text
