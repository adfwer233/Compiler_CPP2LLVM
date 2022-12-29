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

        #load param
        self.loadParam = True

        #end if block
        self.endIf = None
        self.Module.triple="x86_64-pc-linux"

    def visitInitVarBlock(self, ctx: cppLexerParser.InitVarBlockContext):
        print(ctx.myType())
        valType = self.visit(ctx.myType())
        for idText, expr in zip(ctx.myID(), ctx.expr()):
            exprRes = self.visit(expr)
            print(idText.getText(), expr.getText(), exprRes['value'])
            if self.symbolTable.get_current_level() == 0: 
                globalVar = GlobalVariable(self.Module, valType, idText.getText())
                globalVar.linkage = 'internal'
                globalVar.initializer = exprRes['value']
                self.symbolTable.addGlobal(idText.getText(), SymbolItem(valType, globalVar))
            else:
                builder = self.Builders[-1]
                localVar = builder.alloca(valType, name = idText.getText())
                builder.store(exprRes['value'], localVar)
                self.symbolTable.addLocal(idText.getText(), SymbolItem(valType, localVar))
        print(self.symbolTable.table)
        return
    
    def visitAssignBlock(self, ctx: cppLexerParser.AssignBlockContext):
        print(ctx.getChild(0).getText())
        print("assign block")

        # TODO: add array assign
        tmploadParam = self.loadParam
        self.loadParam = False
        leftRes = self.visit(ctx.getChild(0))
        self.loadParam = tmploadParam

        builder = self.Builders[-1]
        exprRes = self.visit(ctx.expr())
        builder.store(exprRes['value'], leftRes['value'])

    def visitInitArrayBlock(self, ctx:cppLexerParser.InitArrayBlockContext):
        # initArrayBlock : myType myID '[' myInt ']'('=' '[' expr (',' expr)* ']')?';';
        type = self.visit(ctx.getChild(0))
        ID = ctx.getChild(1).getText()
        length = int(ctx.getChild(3).getText())
        if self.symbolTable.get_current_level() == 0:
            newArr = GlobalVariable(self.Module, ir.ArrayType(type, length), name=ID)
            newArr.linkage = 'internal'
            newArr.initializer = ir.Constant(ir.ArrayType(type, length), None)
        else:
            builder = self.Builders[-1]
            newArr = builder.alloca(ir.ArrayType(type, length), name=ID)

        symbolItem = SymbolItem(ir.ArrayType(type, length), newArr)
        self.symbolTable.addLocal(ID, symbolItem)
        count = ctx.getChildCount()
        if count > 6:
            childToVisit = 7
            index = 0
            builder = self.Builders[-1]
            while index < length and childToVisit < count:
                address = builder.gep(newArr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), index)])
                valueToStore = self.visit(ctx.getChild(childToVisit))['value']
                builder.store(valueToStore, address)
                childToVisit += 2
                index += 1
        print(self.symbolTable.table)
        return
    def visitInt(self, ctx: cppLexerParser.IntContext):
        print("visit Int")
        if ctx.getChild(0).getText == '-':
            intRes = self.visit(ctx.getChild(1))
            builder = self.Builders[-1]
            res = builder.neg(intRes['value'])
            return {
                'type': intRes['type'], 
                'value': res
            }
        return self.visit(ctx.getChild(0))
    
    def visitDouble(self, ctx:cppLexerParser.DoubleContext):
        if ctx.getChild(0).getText == '-':
            intRes = self.visit(ctx.getChild(1))
            builder = self.Builders[-1]
            res = builder.neg(intRes['value'])
            return {
                'type': intRes['type'], 
                'value': res
            }
        return self.visit(ctx.getChild(0))

    def visitChar(self, ctx: cppLexerParser.CharContext):
        return self.visit(ctx.getChild(0))

    def visitMulDiv(self, ctx: cppLexerParser.MulDivContext):
        builder = self.Builders[-1]
        operand1 = self.visit(ctx.getChild(0))
        operand2 = self.visit(ctx.getChild(2))
        if ctx.getChild(1).getText() == '*':
            res = builder.mul(operand1['value'], operand2['value'])
        elif ctx.getChild(1).getText() == '/':
            res = builder.sdiv(operand1['value'], operand2['value'])
        elif ctx.getChild(1).getText() == '%':
            res = builder.srem(operand1['value'], operand2['value'])
        return {
            'type': operand1['type'],
            'value': res
        }

    def visitAddSub(self, ctx: cppLexerParser.AddSubContext):
        print("visit operations")
        #TODO: operator priority

        builder = self.Builders[-1]
        operand1 = self.visit(ctx.getChild(0))
        operand2 = self.visit(ctx.getChild(2))
        if ctx.getChild(1).getText() == '+':
            res = builder.add(operand1['value'], operand2['value'])
        elif ctx.getChild(1).getText() == '-':
            res = builder.sub(operand1['value'], operand2['value'])
        return {
            'type': operand1['type'],
            'value': res
        }
    
    def visitRelop(self, ctx: cppLexerParser.RelopContext):
        print("visit relop", ctx.getChild(1).getText())
        builder = self.Builders[-1]
        operand1 = self.visit(ctx.getChild(0))
        operand2 = self.visit(ctx.getChild(2))

        # TODO: add double
        res = builder.icmp_signed(ctx.getChild(1).getText(), operand1['value'], operand2['value'])
        return {
            'type': ir.IntType(1),
            'value': res
        }

    def visitAnd(self, ctx: cppLexerParser.AndContext):
        operand1 = self.exprToBool(self.visit(ctx.getChild(0)))
        operand2 = self.exprToBool(self.visit(ctx.getChild(2)))
        builder = self.Builders[-1]
        res = builder.and_(operand1['value'], operand2['value'])
        return {
            'type': ir.IntType(1),
            'value': res
        }

    def visitOr(self, ctx: cppLexerParser.OrContext):
        operand1 = self.exprToBool(self.visit(ctx.getChild(0)))
        operand2 = self.exprToBool(self.visit(ctx.getChild(2)))
        builder = self.Builders[-1]
        res = builder.or_(operand1['value'], operand2['value'])
        return {
            'type': ir.IntType(1),
            'value': res
        }

    def visitParens(self, ctx: cppLexerParser.ParensContext):
        return self.visit(ctx.getChild(0))

    def visitBool(self, ctx:cppLexerParser.BoolContext):
        if ctx.getText() == 'true':
            return {
                'type': ir.IntType(1),
                'value': ir.Constant(ir.IntType(1), 1)
            }
        else:
            return {
                'type': ir.IntType(1),
                'value': ir.Constant(ir.IntType(1), 0)
            }

    def visitIdentifier(self, ctx: cppLexerParser.IdentifierContext):
        return self.visit(ctx.getChild(0))

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

        functionReturn = self.visit(ctx.myBlock())
        if not self.Builders[-1].block.is_terminated:
            self.Builders[-1].ret_void()

        self.symbolTable.exitScope()
        
        return functionReturn

    def visitReturnBlock(self, ctx: cppLexerParser.returnBlock):
        builder = self.Builders[-1]
        if ctx.getChildCount() == 2:
            res = builder.ret_void()
            return {
                'type': ir.VoidType(),
                'value': res
            }
        else:
            exprRes = self.visit(ctx.getChild(1))
            res = builder.ret(exprRes['value'])
            return {
                'type': ir.VoidType(),
                'value': res
            }

    def visitMyBlock(self, ctx: cppLexerParser.MyBlockContext):
        self.symbolTable.enterScope()
        super().visitMyBlock(ctx)
        self.symbolTable.exitScope()
        print("testasdf")
        return

    def visitMyType(self, ctx: cppLexerParser.MyTypeContext):
        text = ctx.getText()
        if text == 'int':
            return ir.IntType(32)
        elif text == 'bool':
            return ir.IntType(1)
        elif text == 'char':
            return ir.IntType(8)
        elif text == 'double':
            return ir.DoubleType()


    def visitMyInt(self, ctx: cppLexerParser.MyIntContext):
        print(ctx.getText())
        return {
            'type': ir.IntType(32),
            'value': ir.Constant(ir.IntType(32), int(ctx.getText()))
        }

    def visitMyDouble(self, ctx: cppLexerParser.MyDoubleContext):
        return {
            'type': ir.DoubleType(),
            'value': ir.Constant(ir.DoubleType(), float(ctx.getText()))
        }

    def visitMyID(self, ctx: cppLexerParser.MyIDContext):
        idName = ctx.getText()
        item = self.symbolTable.getSymbolItem(idName)
        builder = self.Builders[-1]
        print(item.get_type())
        if self.loadParam == True:
            return {
                'type': item.get_type(),
                'value': builder.load(item.get_value())
            }
        else:
            return {
                'type': item.get_type(),
                'value': item.get_value()
            }

    def visitMyChar(self, ctx: cppLexerParser.MyCharContext):
        print("my char " * 5)
        return {
            'type': ir.IntType(8),
            'value': ir.Constant(ir.IntType(8), ord(ctx.getText()[1]))
        }

    def visitMyArray(self, ctx: cppLexerParser.MyArrayContext):
        tmploadParam = self.loadParam
        self.loadParam = False
        res = self.visit(ctx.getChild(0))  # identifier
        self.loadParam = tmploadParam

        if isinstance(res['type'], ir.types.ArrayType):
            builder = self.Builders[-1]

            tmploadParam = self.loadParam
            self.loadParam = True
            operand = self.visit(ctx.getChild(2))
            self.loadParam = tmploadParam
            
            intZero = ir.Constant(ir.IntType(32), 0)
            returnRes = builder.gep(res['value'], [intZero, operand['value']], inbounds=True)

            if self.loadParam:
                returnRes = builder.load(returnRes)
            return {
                'type': res['type'].element,
                'value': returnRes,
            }

    def visitCondition(self, ctx: cppLexerParser.ConditionContext):
        print("visit condition")
        result = self.visit(ctx.getChild(0)) #cond
        return self.exprToBool(result)


    def visitIfBlock(self, ctx: cppLexerParser.IfBlockContext):
        '''
        ifBlock : myIf (myElif)* (myElse)?;
        '''
        builder = self.Builders[-1]
        ifblock = builder.append_basic_block()
        endifblock = builder.append_basic_block()
        builder.branch(ifblock)

        #load ifblock
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(ifblock))

        #handle endifblock
        tmpendif = self.endIf
        self.endIf = endifblock

        length = ctx.getChildCount()
        for i in range(length):
            self.visit(ctx.getChild(i)) #handle if elif else

        self.endIf = tmpendif

        #if finish route to endif block
        tmpbuilder = self.Builders.pop()
        if not tmpbuilder.block.is_terminated:
            tmpbuilder.branch(endifblock)

        self.Builders.append(ir.IRBuilder(endifblock))

        return

    def visitMyIf(self, ctx: cppLexerParser.MyIfContext):
        '''
        myIf : 'if' '(' condition ')' myBlock;
        '''
        self.symbolTable.enterScope()

        #if block: true or false
        builder = self.Builders[-1]
        trueblk = builder.append_basic_block()
        falseblk = builder.append_basic_block()

        #route block base on the condition result
        result = self.visit(ctx.getChild(2))
        builder.cbranch(result['value'], trueblk, falseblk)

        #condition true body
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(trueblk))
        self.visit(ctx.getChild(4)) # body

        if not self.Builders[-1].block.is_terminated:
            self.Builders[-1].branch(self.endIf)
        
        #handle condition false
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(falseblk))
        self.symbolTable.exitScope()

        return

    def visitMyElif(self, ctx: cppLexerParser.MyElifContext):
        '''
        myElif : 'else' 'if' '(' condition ')' block;
        '''
        # same as if there are false and true block
        self.symbolTable.enterScope()
        builder = self.Builders[-1]
        trueblk = builder.append_basic_block()
        falseblk = builder.append_basic_block()

        #route block base on condition result
        result = self.visit(ctx.getChild(3))
        builder.cbranch(result['value'], trueblk, falseblk)

        #condition true -> trueblk
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(trueblk))
        self.visit(ctx.getChild(5)) # body

        if not self.Builders[-1].block.is_terminated:
            self.Builders[-1].branch(self.endIf)

        #condition false
        self.Builders.pop()
        self.Builders.append(ir.builder(falseblk))
        
        self.symbolTable.exitScope()

        return

    def visitMyElse(self, ctx: cppLexerParser.MyElseContext):
        '''
        myElse : 'else' myBlock;
        '''

        #directly handle mybody
        self.symbolTable.enterScope()
        self.visit(ctx.getChild(1)) # body
        self.symbolTable.exitScope()

        return
    
    def visitWhileBlock(self, ctx: cppLexerParser.WhileBlockContext):
        # whileBlock : 'while' '(' condition ')' myBlock;
        self.symbolTable.enterScope()
        builder = self.Builders[-1]

        whileCon = builder.append_basic_block()
        whileBody = builder.append_basic_block()
        whileEnd = builder.append_basic_block()

        builder.branch(whileCon)

        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(whileCon))

        result = self.visit(ctx.getChild(2)) #cond
        self.Builders[-1].cbranch(result['value'], whileBody, whileEnd)

        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(whileBody))
        print(ctx.getChild(4).getText())
        self.visit(ctx.getChild(4)) #body

        self.Builders[-1].branch(whileCon) #redetermine cond

        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(whileEnd))

        self.symbolTable.exitScope()

        return

    def visitForBlock(self, ctx: cppLexerParser.ForBlockContext):
        '''
        forBlock : 'for' '(' for1 ';' condition ';' for3 ')' myblock;
        '''
        print("visit for block here")
        self.symbolTable.enterScope()

        self.visit(ctx.getChild(2))

        builder = self.Builders[-1]
        forCond = builder.append_basic_block()
        forbody = builder.append_basic_block()
        forEnd = builder.append_basic_block()

        #Cond determine
        builder.branch(forCond)
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(forCond))

        #determine whether jump to end or body
        print(ctx.getChildCount())
        print(ctx.getText())
        print(ctx.getChild(4).getText())
        result = self.visit(ctx.getChild(4)) #Cond blk
        self.Builders[-1].cbranch(result['value'], forbody, forEnd)
        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(forbody))

        #handle body
        if (ctx.getChildCount() == 9):
            self.visit(ctx.getChild(8)) #main body
        
        #handle step
        self.visit(ctx.getChild(6)) #step blk

        #loop once then check condition again
        self.Builders[-1].branch(forCond)

        self.Builders.pop()
        self.Builders.append(ir.IRBuilder(forEnd))

        self.symbolTable.exitScope()

        return

    def visitFor1(self, ctx: cppLexerParser.For1Context):
        '''
        for1 : myID '=' expr (',' for1)?|;
        '''
        length = ctx.getChildCount()
        if length==0:
            return
        
        Paramload = self.loadParam
        self.loadParam = False
        res0 = self.visit(ctx.getChild(0)) #myID
        self.loadParam = Paramload

        #Visit expr
        res1 = self.visit(ctx.getChild(2)) # expr
        #TODO assign convert
        self.Builders[-1].store(res1['value'], res0['value'])

        if length > 3:
            self.visit(ctx.getChild(4))
        
        return
    
    def visitFor3(self, ctx: cppLexerParser.For3Context):
        '''
        for3 : myID '=' expr (',' for3)?|;
        '''
        length = ctx.getChildCount()
        if length == 0:
            return
        
        Paramload = self.loadParam
        self.loadParam = False
        res0 = self.visit(ctx.getChild(0)) #myID
        self.loadParam = Paramload

        # visit expr
        res1 = self.visit(ctx.getChild(2)) # expr
        #TODO: assign convert
        self.Builders[-1].store(res1['value'], res0['value'])

        if length > 3:
            self.visit(ctx.getChild(4))
        return


    # functions for type cast

    def exprToBool(self, operandDict):
        operandType = operandDict['type']
        builder = self.Builders[-1]
        if operandType in [ir.IntType(8), ir.IntType(32)]:
            res = builder.icmp_signed('==', operandDict['value'], ir.Constant(operandType, 0))
            return {
                'type': ir.IntType(1),
                'name': res
            }
        return operandDict


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

    ll = str(visitor.Module)
    # # stream.getText()
    # stream.fill()
    # for token in stream.tokens:
    #     print(token)

    print(ll)

    with open("./res.ll", 'w') as f:
        f.write(ll)

if __name__ == '__main__':
    main(sys.argv)