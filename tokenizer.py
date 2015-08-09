"""
Contains the Tokenizer for the Lambda Calculus.
"""
import os.path
import string

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Tokenizer(object):
    """
        Tokenize a file.
    """

    def __init__(self, filename):
        # check that filename is correct.
        assert os.path.isfile(filename), filename + ": is not a valid file."

        # read file, store contents
        with open(filename, 'r') as f:
            self.src = f.read()

        # capture the generator
        self.token_stream = None

        # This field is either None, or corresponds to the very next token
        # to be removed from the Tokenizer stream.
        self.on_deck = None

        # A list of token regexes. Used to match input.
        self.token_classes = []

    def add_token_class(self, rep, regex):
        self.token_classes.append((rep, regex))

    def tokenize():

        def _tokens():
            """
                Produce a generator for extracting tokens from the source
                file.
            """
            token = ''
            for c in src:
                if c in string.whitespace or Tokenizer._syntax_token(c):

                    if len(token) > 0:
                        yield token
                        token = ''

                    if Tokenizer._syntax_token(c):
                        yield c

                else:
                    token += c

            if len(token) > 0:
                yield token

        self._token_stream = _tokens()

    def peek(self):
        """
            Produce the next token, without removal.
        """
        if self._token_stream is None:
            raise Exception(
                'Tokenizer tokenstream has not been initialized.'
                'Call tokenize().')
        if self.on_deck is None:
            self.on_deck = next(self._token_stream, None)
        return self.on_deck

    def pull(self):
        """
            Produce the next token, and remove token.
        """
        if self._token_stream is None:
            raise Exception(
                'Tokenizer tokenstream has not been initialized.'
                'Call tokenize().')
        if self.on_deck is None:
            return next(self._token_stream, None)
        else:
            res, self.on_deck = self.on_deck, None
            return res

