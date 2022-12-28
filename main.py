import sys
from antlr4 import *
from antlr4.tree.Trees import Trees
from src.grammar.cppLexerLexer import cppLexerLexer
from src.grammar.cppLexerParser import cppLexerParser
from src.grammar.cppLexerVisitor import cppLexerVisitor

from io import StringIO
from antlr4.Token import Token
from antlr4.Utils import escapeWhitespace
from antlr4.tree.Tree import RuleNode, ErrorNode, TerminalNode, Tree, ParseTree

from symbolTable import SymbolTable
from llvmlite import ir

class MyTrees(Trees):
    def toStringTree(self, t: Tree, ruleNames: list = None, prefix='', recog: Parser = None):
        if recog is not None:
            ruleNames = recog.ruleNames
        child = escapeWhitespace(self.getNodeText(t, ruleNames), False)
        if t.getChildCount() == 0:
            return child
        with StringIO() as buf:
            if (child != 'prog'):
                buf.write('\n')
                buf.write(prefix + '-' + '\n')
            buf.write(prefix + child)
            buf.write(':')
            for i in range(0, t.getChildCount()):
                if i > 0:
                    buf.write('')
                buf.write(self.toStringTree(t.getChild(i), ruleNames, prefix + '  '))
            buf.write(' ')
            return buf.getvalue()

class myCppVisitor(cppLexerVisitor):
    def __init__(self):
        super(cppLexerVisitor, self).__init__()

        self.Module = ir.Module()
        self.Builders = []
        self.symbolTable = SymbolTable()

        
    def visitInitBlock(self, ctx: cppLexerParser.InitBlockContext):
        return super().visitInitBlock(ctx)
    

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = cppLexerLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = cppLexerParser(stream)
    tree = parser.prog()
    mytree = MyTrees()
    print(mytree.toStringTree(tree, None, '***', parser))

    # # stream.getText()
    # stream.fill()
    # for token in stream.tokens:
    #     print(token)


if __name__ == '__main__':
    main(sys.argv)