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

from symbolTable import SymbolTable, SymbolItem
from llvmlite import ir
from llvmlite.ir.values import GlobalVariable, ReturnValue

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


    def visitInitVarBlock(self, ctx: cppLexerParser.InitVarBlockContext):
        print(ctx.myType())
        valType = self.visit(ctx.myType())
        for idText, expr in zip(ctx.myID(), ctx.expr()):
            print(idText.getText(), expr.getText())
            if self.symbolTable.get_current_level() == 0: 
                globalVar = GlobalVariable(self.Module, valType, idText.getText())
                globalVar.linkage = 'internal'
                globalVar.initializer = ir.Constant(valType, expr) # TODO: add expr translation
                self.symbolTable.addGlobal(idText.getText(), SymbolItem(valType, globalVar))
            else:
                builder = self.Builders[-1]
                localVar = builder.alloca(valType, idText.getText())
                builder.store(expr, localVar)
                self.symbolTable.addLocal(idText.getText(), SymbolItem(valType, localVar))
        print(self.symbolTable.table)

    def visitParams(self, ctx: cppLexerParser.ParamsContext):
        parameterList = []
        for param in ctx.param():
            paramType = self.visit(param.myType())
            paramID = param.myID().getText()
            parameterList.append((paramType, paramID))
        return parameterList

    def visitMyFunction(self, ctx: cppLexerParser.MyFunctionContext):
        returnType = self.visit(ctx.myType())
        funcName = ctx.myID().getText()
        parameterList = tuple(self.visit(ctx.params()))
        parameterTypeList = tuple(param[0] for param in parameterList)
        print(returnType, funcName, parameterList)
        
        llvmFuncType = ir.FunctionType(returnType, parameterTypeList)
        llvmFunc = ir.Function(self.Module, llvmFuncType, funcName)
        self.symbolTable.addGlobal(funcName, SymbolItem(llvmFuncType, llvmFunc))
        
        block = llvmFunc.append_basic_block(funcName)
        builder = ir.IRBuilder(block)
        self.Builders.append(builder)
        self.symbolTable.enterScope()

        for param, funcArg in zip(parameterList, llvmFunc.args):
            address = builder.alloca(funcArg.type, name=param[1])
            builder.store(funcArg, address)
            self.symbolTable.addLocal(param[1], SymbolItem(param[0], address))

        # functionReturn = self.visit(ctx.myBlock)
        if not self.Builders[-1].block.is_terminated:
            self.Builders[-1].ret_void()

        self.symbolTable.exitScope()
        
        return functionReturn

    def visitMyBlock(self, ctx: cppLexerParser.MyBlockContext):
        pass

    def visitMyType(self, ctx: cppLexerParser.MyTypeContext):
        text = ctx.getText()
        if text == 'int':
            return ir.IntType(32)

    def visitMyInt(self, ctx: cppLexerParser.MyIntContext):
        print(ctx.getText())
        return super().visitMyInt(ctx)

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = cppLexerLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = cppLexerParser(stream)
    tree = parser.prog()
    mytree = MyTrees()
    print(mytree.toStringTree(tree, None, '***', parser))

    visitor = myCppVisitor()
    visitor.visit(tree)

    print(str(visitor.Module))
    # # stream.getText()
    # stream.fill()
    # for token in stream.tokens:
    #     print(token)


if __name__ == '__main__':
    main(sys.argv)