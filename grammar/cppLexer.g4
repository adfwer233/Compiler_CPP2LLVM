grammar cppLexer;

prog : (include)* (myNamespace)* (myFunction | initVarBlock | initArrayBlock | structBlock)*;

//include
include : '#include' '<' LIB '>';

//namespace
myNamespace : 'using namespace std;';

//函数
myFunction : (myType | myVoid) myID '(' params ')' '{' myFuncmyBody '}';

//参数
params : param (','param)* |;
param : myType myID;

//函数体
myFuncmyBody : myBody myReturn;
myBody : (myBlock | func';')*;
myReturn : 'return' (myInt|myID)?';';

//结构体
structBlock : myStruct '{' (structParam)+ '}'';';
structParam : myType (myID | myArray) (',' (myID | myArray))* ';';

//语句块
// todo while & for
myBlock : initVarBlock | initArrayBlock | assignBlock | ifBlock | myReturn | initStructBlock | whileBlock | forBlock;

//初始化
initVarBlock : myType myID ('=' expr) ? (',' myID ('=' expr)?)* ';';
initArrayBlock : myType myID '[' myInt ']'('=' myArray)?';';
initStructBlock : myStruct (myID | myArray)';';
//赋值
assignBlock : ((myArray | myID | structMem) '=')+ expr ';';


//if
ifBlock : myIf (myElif)* (myElse)?;
myIf : 'if' '(' condition ')' '{' myBody '}';
myElif : 'else' 'if' '(' condition ')' '{' myBody '}';
myElse : 'else' '{' myBody '}';

//while
whileBlock : 'while' '(' condition ')' '{' myBody '}';

//for
forBlock : 'for' '(' for1 ';' condition ';' for3 ')' '{' myBody '}';
for1 : (myType)? myID '=' expr;
for3 : myID '=' expr;

condition : expr;

expr
    : '(' expr ')'
    | expr op=('+' | '-' | '*' | '/' | '%') expr
    | expr op=('==' | '!=' | '<' | '<=' | '>' | '>=') expr
    | op='!' expr
    | expr '&&' expr
    | expr '||' expr
    | (op='-')? myInt
    | (op='-')? myDouble
    | myChar
    | myArray
    | myString
    | myID
    | structMem
    | func
    | buildin
    ;

//todo more buildin
buildin : 'endl';

myType : 'int' | 'double' | 'char' | 'string';

myArray : (myID)? '[' expr (','expr)* ']';

myVoid : 'void';

myID : ID;

myInt : INT;

myDouble : DOUBLE;

myChar : CHAR;

myString : STRING;

myStruct : 'struct' myID;

structMem : (myID | myArray)'.'(myID | myArray);

// todo more func
func : (coutFunc | cinFunc);

coutFunc : ('cout' ('<<' expr)+);

cinFunc : ('cin' ('>>' expr)+);

ID : [a-zA-Z_][0-9a-zA-Z_]*;

INT : [0-9]+;

DOUBLE : [0-9]+'.'[0-9]+;

CHAR : '\''.'\'';

STRING : '"'.*?'"';

LIB : [a-zA-Z]+('.h')?;

// Directive
Directive: '#' ~ [\n]* -> channel (HIDDEN);

// Literals to skip
Whitespace: [ \t]+ -> skip;

Newline: ('\r' '\n'? | '\n') -> skip;

BlockComment: '/*' .*? '*/' -> skip;

LineComment: '//' ~ [\r\n]* -> skip;