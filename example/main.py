import sys
from antlr4 import *
from CPP14Lexer import CPP14Lexer
from CPP14Parser import CPP14Parser
from CPP14ParserListener import CPP14ParserListener


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = CPP14Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    # parser = CPP14Parser(stream)
    # tree = parser.translationUnit()
    # print(tree.toStringTree(recog=parser))

    print(stream.getText())
    for item in stream.tokens:
        print(item)


if __name__ == '__main__':
    main(sys.argv)