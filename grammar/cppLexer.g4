grammar cppLexer;

prog : (include)* (myNamespace)* (myFunction | initBlock | arrayBlock)*;

//include
include : '#include' '<' LIB '>';

//namespace
myNamespace : 'using namespace std;';

//函数
myFunction : (myType | myVoid) myID '(' params ')' '{' myFuncBody '}';

//参数
params : param (','param)* |;
param : myType myID;

//函数体
myFuncBody : body myReturn;
body : (myBlock | func';')*;
myReturn : 'return' (myInt|myID)?';';

//语句块
// todo while & for
myBlock : initBlock | arrayBlock | assignBlock | ifBlock | myReturn;

//初始化
initBlock : myType myID ('=' expr) ? (',' myID ('=' expr)?)* ';';
arrayBlock : (((myType myID '[' myInt ']') '=' '[' expr (',' expr)? ']') | ('char' myID '[]' '=' expr)) ';';

//赋值
assignBlock : ((myArray | myID ) '=')+ expr ';';

//if
ifBlock : myIf (myElif)* (myElse)?;
myIf : 'if' '(' condition ')' '{' body '}';
myElif : 'else' 'if' '(' condition ')' '{' body '}';
myElse : 'else' '{' body '}';

condition : expr;

expr
    : '(' expr ')'
    | op='!' expr
    | expr op=('+' | '-' | '*' | '/' | '%') expr
    | expr op=('==' | '!=' | '<' | '<=' | '>' | '>=') expr
    | expr '&&' expr
    | expr '||' expr
    | (op='-')? myInt
    | (op='-')? myDouble
    | myChar
    | myString
    | myID
    | func
    | buildin
    ;

//todo more buildin
buildin : 'endl';

myType : 'int' | 'double' | 'char' | 'string';

myArray : myID '[' (myInt)? ']';

myVoid : 'void';

myID : ID;

myInt : INT;

myDouble : DOUBLE;

myChar : CHAR;

myString : STRING;

// todo more func
func : (coutFunc | cinFunc);

coutFunc : ('cout' ('<<' expr)+) ';';

cinFunc : ('cin' ('>>' expr)+) ';';

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