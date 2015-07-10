import os.path
import string

class Tokenizer(object):
    """Tokenize a file formated for the lambda calculus"""

    OPEN = '('
    CLOSE = ')'
    ABS = ':'
    BQUO = '`'

    def __init__(self, filename):
        assert os.path.isfile(filename), filename + ": is not a valid file."
        with open(filename, 'r') as f:
            self.src = f.read()

    @classmethod
    def syntax_token(cls, c):
        return c in ([cls.OPEN,
                      cls.CLOSE,
                      cls.ABS,
                      cls.BQUO])

    def tokenize(self):
        """
            Return tokens corresponding to the file
        """
        tokens = []
        token = ''

        for c in self.src:
            if c in string.whitespace or Tokenizer.syntax_token(c):

                if len(token) > 0:
                    tokens.append(token)
                    token = ''

                if c == Tokenizer.OPEN:
                    tokens.append(Tokenizer.OPEN)
                elif c == Tokenizer.CLOSE:
                    tokens.append(Tokenizer.CLOSE)
                elif c == Tokenizer.ABS:
                    tokens.append(Tokenizer.ABS)
                elif c == Tokenizer.BQUO:
                    tokens.append(Tokenizer.BQUO)
            else:
                token += c

        if len(token) > 0:
            tokens.append(token)

        return tokens

