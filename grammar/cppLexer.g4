grammar cppLexer;

prog : (include)* (myNamespace)* (myFunction | initVarBlock | initArrayBlock | structBlock)*;

//include
include : '#include' '<' LIB '>';

//namespace
myNamespace : 'using namespace std;';

//函数
myFunction : (myType | myVoid) myID '(' params ')' myBlock;

//参数
params : param (','param)* |;
param : myType myID;

//函数体
myBody : (myBlock | func';')*;
returnBlock : 'return' (myInt|myID)?';';

//结构体
structBlock : myStruct '{' (structParam)+ '}'';';
structParam : myType (myID | myArray) (',' (myID | myArray))* ';';

//语句块
// todo while & for
myBlock : LBRACE (statement)* RBRACE;

statement: 
    initVarBlock 
    | initArrayBlock 
    | assignBlock 
    | ifBlock 
    | returnBlock
    | whileBlock 
    | forBlock
    | expr? ';'
    | myBlock;

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
    : '(' expr ')'                                              #parens
    | expr op=('*' | '/' | '%') expr                            #mulDiv
    | expr op=('+' | '-') expr                                  #addSub
    | expr op=('==' | '!=' | '<' | '<=' | '>' | '>=') expr      #relop
    | op='!' expr                   #neg
    | expr '&&' expr                #and
    | expr '||' expr                #or
    | (op='-')? myInt               #int
    | (op='-')? myDouble            #double
    | myChar                        #char
    | myArray                       #array
    | myString                      #string
    | myID                          #identifier
    | structMem                     #structmember
    | func                          #function
    ;

//todo more buildin
buildin : 'endl';

myType : 'int' | 'double' | 'char' | 'string' | 'bool';

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

LBRACE: '{';

RBRACE: '}';