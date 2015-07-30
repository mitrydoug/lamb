"""
Contains the Tokenizer for the Lambda Calculus.
"""
import os.path
import string

class Tokenizer(object):
    """Tokenize a file formated for the lambda calculus"""

    # The atomic syntax tokens of the lambda calculus
    OPEN = '('
    CLOSE = ')'
    ABS = ':'
    BQUO = '`'
    EQ = '='
    COMMA = ','

    def __init__(self, filename):
        # check that filename is correct.
        assert os.path.isfile(filename), filename + ": is not a valid file."
        # read file, store contents
        with open(filename, 'r') as f:
            src = f.read()

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

        # capture the generator
        self.tokenstream = _tokens()
        # This field is either None, or corresponds to the very next token
        # to be removed from the Tokenizer stream.
        self.onDeck = None

    @classmethod
    def _syntax_token(cls, c):
        """Is the character c a syntax token of the lambda calculus?"""
        return c in ([cls.OPEN,
                      cls.CLOSE,
                      cls.ABS,
                      cls.BQUO,
                      cls.EQ,
                      cls.COMMA])

    def peek(self):
        """
            Produce the next token, without removal.
        """
        if self.onDeck is None:
            self.onDeck = next(self.tokenstream, None)
        return self.onDeck

    def pull(self):
        """
            Produce the next token, and remove token.
        """
        if self.onDeck is None:
            return next(self.tokenstream, None)
        else:
            res, self.onDeck = self.onDeck, None
            return res

