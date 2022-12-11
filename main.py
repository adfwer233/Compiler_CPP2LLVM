import sys
from antlr4 import *
from src.grammar.cppLexerLexer import cppLexerLexer
from src.grammar.cppLexerParser import cppLexerParser


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = cppLexerLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = cppLexerParser(stream)
    tree = parser.prog()
    print(tree.toStringTree(recog=parser))

    # # stream.getText()
    # stream.fill()
    # for token in stream.tokens:
    #     print(token)


if __name__ == '__main__':
    main(sys.argv)