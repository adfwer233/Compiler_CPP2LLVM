import sys
from antlr4 import *
from antlr4.tree.Trees import Trees
from src.grammar.SimpleCppLexer import SimpleCppLexer
from src.grammar.SimpleCppParser import SimpleCppParser
from src.grammar.SimpleCppVisitor import SimpleCppVisitor

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

class myCppVisitor(SimpleCppVisitor):
    def __init__(self):
        super(SimpleCppVisitor, self).__init__()

        self.Module = ir.Module()
        self.Builders = []
        self.symbolTable = SymbolTable()

        #load param
        self.loadParam = True

        #end if block
        self.endIf = None
        self.Module.triple="x86_64-pc-linux"

        #function list
        self.functionDict = dict()

        self.strConstIndex = 0
    def visitInitVarBlock(self, ctx: SimpleCppParser.InitVarBlockContext):
        valType = self.visit(ctx.myType())
        for idText, expr in zip(ctx.myID(), ctx.expr()):
            exprRes = self.visit(expr)
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
        return
    
    def visitAssignBlock(self, ctx: SimpleCppParser.AssignBlockContext):

        # TODO: add array assign
        tmploadParam = self.loadParam
        self.loadParam = False
        leftRes = self.visit(ctx.getChild(0))
        self.loadParam = tmploadParam

        builder = self.Builders[-1]
        exprRes = self.visit(ctx.expr())
        builder.store(exprRes['value'], leftRes['value'])

    def visitInitArrayBlock(self, ctx:SimpleCppParser.InitArrayBlockContext):
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
        return
    def visitInt(self, ctx: SimpleCppParser.IntContext):
        if ctx.getChild(0).getText() == '-':
            intRes = self.visit(ctx.getChild(1))
            builder = self.Builders[-1]
            res = builder.neg(intRes['value'])
            return {
                'type': intRes['type'], 
                'value': res
            }
        return self.visit(ctx.getChild(0))
    
    def visitDouble(self, ctx:SimpleCppParser.DoubleContext):
        if ctx.getChild(0).getText() == '-':
            intRes = self.visit(ctx.getChild(1))
            builder = self.Builders[-1]
            res = builder.neg(intRes['value'])
            return {
                'type': intRes['type'], 
                'value': res
            }
        return self.visit(ctx.getChild(0))

    def visitChar(self, ctx: SimpleCppParser.CharContext):
        return self.visit(ctx.getChild(0))


    def visitMulDiv(self, ctx: SimpleCppParser.MulDivContext):
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

    def visitAddSub(self, ctx: SimpleCppParser.AddSubContext):
        print("visit operations")
        #TODO: operator priority

        builder = self.Builders[-1]
        operand1 = self.visit(ctx.getChild(0))
        operand2 = self.visit(ctx.getChild(2))
        print("????" * 10, ctx.getChild(0).getText(), ctx.getChild(2).getText())
        print(ctx.getText())
        if ctx.getChild(1).getText() == '+':
            res = builder.add(operand1['value'], operand2['value'])
        elif ctx.getChild(1).getText() == '-':
            res = builder.sub(operand1['value'], operand2['value'])
        return {
            'type': operand1['type'],
            'value': res
        }
    
    def visitRelop(self, ctx: SimpleCppParser.RelopContext):
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

    def visitAnd(self, ctx: SimpleCppParser.AndContext):
        operand1 = self.exprToBool(self.visit(ctx.getChild(0)))
        operand2 = self.exprToBool(self.visit(ctx.getChild(2)))
        builder = self.Builders[-1]
        res = builder.and_(operand1['value'], operand2['value'])
        return {
            'type': ir.IntType(1),
            'value': res
        }

    def visitOr(self, ctx: SimpleCppParser.OrContext):
        operand1 = self.exprToBool(self.visit(ctx.getChild(0)))
        operand2 = self.exprToBool(self.visit(ctx.getChild(2)))
        builder = self.Builders[-1]
        res = builder.or_(operand1['value'], operand2['value'])
        return {
            'type': ir.IntType(1),
            'value': res
        }

    def visitParens(self, ctx: SimpleCppParser.ParensContext):
        return self.visit(ctx.getChild(0))

    def visitBool(self, ctx:SimpleCppParser.BoolContext):
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

    def visitIdentifier(self, ctx: SimpleCppParser.IdentifierContext):
        return self.visit(ctx.getChild(0))

    def visitParams(self, ctx: SimpleCppParser.ParamsContext):
        parameterList = []
        for param in ctx.param():
            if param.DOTS() is None:
                paramType = self.visit(param.myType())
                paramID = param.myID().getText()
                parameterList.append((paramType, paramID))
            else:
                parameterList.append(("varargs", "varargs"))
        return parameterList


    def visitMyFunctionDecl(self, ctx: SimpleCppParser.MyFunctionDeclContext):
        returnType = self.visit(ctx.myType())
        funcName = ctx.myID().getText()
        parameterList = tuple(self.visit(ctx.params()))
        parameterTypeList = tuple(param[0] for param in parameterList)
        is_vararg = "varargs" in parameterTypeList
        print(parameterTypeList)
        if is_vararg:
            if parameterTypeList.count("varargs") > 1:
                raise Exception("too many varargs")
            elif parameterTypeList[-1] != "varargs":
                raise Exception("varargs should be last param")
            parameterTypeList = parameterTypeList[:-1]
        print("asfdasfasdfasdf")
        
        llvmFuncType = ir.FunctionType(returnType, parameterTypeList, var_arg=is_vararg)
        llvmFunc = ir.Function(self.Module, llvmFuncType, funcName)
        self.symbolTable.addGlobal(funcName, SymbolItem(llvmFuncType, llvmFunc))

        if funcName in self.functionDict:
            raise Exception(f"Function redefinition Error!")
        else:
            self.functionDict[funcName] = llvmFunc

    def visitMyFunction(self, ctx: SimpleCppParser.MyFunctionContext):
        print(ctx.getText())
        print(ctx.myType().getText())
        returnType = self.visit(ctx.myType())
        funcName = ctx.myID().getText()
        parameterList = tuple(self.visit(ctx.params()))
        parameterTypeList = tuple(param[0] for param in parameterList)
        print(returnType, funcName, parameterList)
        
        llvmFuncType = ir.FunctionType(returnType, parameterTypeList)
        llvmFunc = ir.Function(self.Module, llvmFuncType, funcName)
        self.symbolTable.addGlobal(funcName, SymbolItem(llvmFuncType, llvmFunc))
        
        block = llvmFunc.append_basic_block(funcName)

        if funcName in self.functionDict:
            raise Exception(f"Function redefinition Error!")
        else:
            self.functionDict[funcName] = llvmFunc

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

    def visitReturnBlock(self, ctx: SimpleCppParser.returnBlock):
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

    def visitMyBlock(self, ctx: SimpleCppParser.MyBlockContext):
        self.symbolTable.enterScope()
        super().visitMyBlock(ctx)
        self.symbolTable.exitScope()
        print("testasdf")
        return

    def visitMyType(self, ctx: SimpleCppParser.MyTypeContext):
        text = ctx.getText()
        if text == 'int':
            return ir.IntType(32)
        elif text == 'bool':
            return ir.IntType(1)
        elif text == 'char':
            return ir.IntType(8)
        elif text == 'double':
            return ir.DoubleType()
        elif text == 'char*':
            return ir.PointerType(ir.IntType(8))
        elif text == 'void':
            return ir.VoidType()
    
    def visitMyVoid(self, ctx: SimpleCppParser.MyVoidContext):
        return ir.VoidType()

    def visitMyInt(self, ctx: SimpleCppParser.MyIntContext):
        print("visit int", ctx.getText())
        return {
            'type': ir.IntType(32),
            'value': ir.Constant(ir.IntType(32), int(ctx.getText()))
        }

    def visitMyDouble(self, ctx: SimpleCppParser.MyDoubleContext):
        return {
            'type': ir.DoubleType(),
            'value': ir.Constant(ir.DoubleType(), float(ctx.getText()))
        }

    def visitMyID(self, ctx: SimpleCppParser.MyIDContext):
        idName = ctx.getText()
        item = self.symbolTable.getSymbolItem(idName)
        builder = self.Builders[-1]
        print(item.get_type())
        if self.loadParam == True and not isinstance(item.get_type(), ir.types.ArrayType):
            return {
                'type': item.get_type(),
                'value': builder.load(item.get_value())
            }
        else:
            return {
                'type': item.get_type(),
                'value': item.get_value()
            }
    
    def visitRefId(self, ctx: SimpleCppParser.RefIdContext):
        tmploadParam = self.loadParam
        self.loadParam = False
        res = self.visit(ctx.myID())
        self.loadParam = tmploadParam
        return res

    def visitRefArray(self, ctx: SimpleCppParser.RefArrayContext):
        tmploadParam = self.loadParam
        self.loadParam = False
        res = self.visit(ctx.myArray())
        self.loadParam = tmploadParam
        return res

    def visitMyChar(self, ctx: SimpleCppParser.MyCharContext):
        print("my char " * 5)
        return {
            'type': ir.IntType(8),
            'value': ir.Constant(ir.IntType(8), ord(ctx.getText()[1]))
        }

    def visitMyArray(self, ctx: SimpleCppParser.MyArrayContext):
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

    def visitCondition(self, ctx: SimpleCppParser.ConditionContext):
        print("visit condition")
        result = self.visit(ctx.getChild(0)) #cond
        return self.exprToBool(result)


    def visitIfBlock(self, ctx: SimpleCppParser.IfBlockContext):
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

    def visitMyIf(self, ctx: SimpleCppParser.MyIfContext):
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

    def visitMyElif(self, ctx: SimpleCppParser.MyElifContext):
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

    def visitMyElse(self, ctx: SimpleCppParser.MyElseContext):
        '''
        myElse : 'else' myBlock;
        '''

        #directly handle mybody
        self.symbolTable.enterScope()
        self.visit(ctx.getChild(1)) # body
        self.symbolTable.exitScope()

        return
    
    def visitWhileBlock(self, ctx: SimpleCppParser.WhileBlockContext):
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

    def visitForBlock(self, ctx: SimpleCppParser.ForBlockContext):
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

    def visitFor1(self, ctx: SimpleCppParser.For1Context):
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
    
    def visitFor3(self, ctx: SimpleCppParser.For3Context):
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
                'value': res
            }
        return operandDict
    
    def arrayToPoint(self, operandDict):
        builder = self.Builders[-1]
        zero = ir.Constant(ir.IntType(32), 0)
        res = builder.gep(operandDict['value'], [zero, zero], inbounds=True)
        return {
            'value': res
        }

    # function call
    def visitFunc(self, ctx: SimpleCppParser.FuncContext):
        '''
        func : (coutFunc | cinFunc | newFunc);
        '''
        return self.visit(ctx.getChild(0))

    # new definied function
    def visitNewFunc(self, ctx: SimpleCppParser.NewFuncContext):
        '''
        newFunc : myID '('((argument | myID)(','(argument | myID))*)?')';
        '''
        builder = self.Builders[-1]
        functionName = ctx.getChild(0).getText() # get function name

        if functionName in self.functionDict:
            func = self.functionDict[functionName]

            length = ctx.getChildCount()
            paramList = []
            i = 2
            while i < length - 1:
                param = self.visit(ctx.getChild(i))
                #TODO param convert
                paramList.append(param['value'])
                i += 2
            returnVar = builder.call(func, paramList)
            res = {
                'type': func.function_type.return_type,
                'value': returnVar
            }
            return res
        else:
            raise Exception("Function hasn't defined!")

    def visitArgument(self, ctx: SimpleCppParser.ArgumentContext):
        '''
        argument: myInt | myDouble | myChar | myString;
        '''

        return self.visit(ctx.getChild(0))
    
    def visitMyString(self, ctx: SimpleCppParser.MyStringContext):
        processedString = ctx.getText().replace('\\n', '\n')
        processedString = processedString[1:-1]
        processedString += '\0'
        Len = len(processedString)
        res = ir.GlobalVariable(self.Module, ir.ArrayType(ir.IntType(8), Len), f".str{self.strConstIndex}")
        self.strConstIndex += 1
        res.global_constant = True
        res.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), Len), bytearray(processedString, 'utf-8'))
        resDict = {
            'type': ir.ArrayType(ir.IntType(8), Len).as_pointer(),
            'value': res
        }
        return self.arrayToPoint(resDict)
    
    def visitString(self, ctx: SimpleCppParser.StringContext):
        return self.visit(ctx.getChild(0))

def main(argv):
    input_stream = FileStream(argv[1])
    outputFile = argv[2]
    lexer = SimpleCppLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = SimpleCppParser(stream)
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

    with open(outputFile, 'w') as f:
        f.write(ll)

if __name__ == '__main__':
    main(sys.argv)