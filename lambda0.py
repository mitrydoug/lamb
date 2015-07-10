#! /usr/bin/env python
import sys
import tokenizer

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage: ./lambda0.py source_file')
        sys.exit(0)
    t = tokenizer.Tokenizer(sys.argv[1])
    print(t.tokenize())

