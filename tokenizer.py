import os.path
import string

class Tokenizer(object):
    """Tokenize a file formated for the lambda calculus"""

    OPEN = '('
    CLOSE = ')'
    ABS = ':'
    BQUO = '`'
    EQ = '='
    COMMA = ','

    def __init__(self, filename):
        assert os.path.isfile(filename), filename + ": is not a valid file."
        with open(filename, 'r') as f:
            self.src = f.read()

    @classmethod
    def syntax_token(cls, c):
        return c in ([cls.OPEN,
                      cls.CLOSE,
                      cls.ABS,
                      cls.BQUO,
                      cls.EQ,
                      cls.COMMA])

    def tokenize(self):
        """
            Return tokens corresponding to the file
        """
        def _tokens():
            token = ''
            for c in self.src:
                if c in string.whitespace or Tokenizer.syntax_token(c):

                    if len(token) > 0:
                        yield token
                        token = ''

                    if Tokenizer.syntax_token(c):
                        yield c

                else:
                    token += c

            if len(token) > 0:
                yield token

        self.tokenstream = _tokens()
        self.onDeck = None

    def peek(self):
        if self.onDeck is None:
            self.onDeck = next(self.tokenstream, None)
        return self.onDeck

    def pull(self):
        if self.onDeck is None:
            return next(self.tokenstream, None)
        else:
            res = self.onDeck
            self.onDeck = None
            return res

