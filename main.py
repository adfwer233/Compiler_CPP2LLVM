import sys
from antlr4 import *
from src.grammar.MyCPPLexer import MyCPPLexer


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = MyCPPLexer(input_stream)
    stream = CommonTokenStream(lexer)

    # parser = CPP14Parser(stream)
    # tree = parser.translationUnit()
    # print(tree.toStringTree(recog=parser))

    # stream.getText()
    stream.fill()
    for token in stream.tokens:
        print(token)


if __name__ == '__main__':
    main(sys.argv)