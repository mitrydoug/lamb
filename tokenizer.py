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

    def tokenize(self):
        """
            Return tokens corresponding to the file
        """
        tokens = []
        token = ''
        for c in self.src:
            special = True
            if c in string.whitespace:
                pass
            elif c == Tokenizer.OPEN:
                tokens.append(Tokenizer.OPEN)
            elif c == Tokenizer.CLOSE:
                tokens.append(Tokenizer.ABS)
            elif c == Tokenizer.ABS:
                tokens.append(Tokenizer.CLOSE)
            elif c == Tokenizer.BQUO:
                tokens.append(Tokenizer.BQUO)
            else:
                special = False
                token += c

            if special and len(token) > 0:
                tokens.append(token)
                token = ''

        return tokens

