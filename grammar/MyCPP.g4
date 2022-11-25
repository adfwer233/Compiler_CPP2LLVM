lexer grammar MyCPP;

// Keywords

Bool: 'bool';

Break: 'break';

Char: 'char';

Const: 'const';

Continue: 'continue';

Do: 'do';

Double: 'double';

Else: 'else';

False_: 'false';

Float: 'float';

For: 'for';

If: 'if';

Int: 'int';

Long: 'long';

Return: 'return';

Sizeof: 'sizeof';

True_: 'true';
// Operators

LeftParen: '(';

RightParen: ')';

LeftBracket: '[';

RightBracket: ']';

LeftBrace: '{';

RightBrace: '}';

Plus: '+';

Minus: '-';

Star: '*';

Div: '/';

Mod: '%';

Caret: '^';

And: '&';

Or: '|';

Tilde: '~';

Not: '!' | 'not';

Assign: '=';

Less: '<';

Greater: '>';

PlusAssign: '+=';

MinusAssign: '-=';

StarAssign: '*=';

DivAssign: '/=';

ModAssign: '%=';

XorAssign: '^=';

AndAssign: '&=';

OrAssign: '|=';

LeftShiftAssign: '<<=';

RightShiftAssign: '>>=';

Equal: '==';

NotEqual: '!=';

LessEqual: '<=';

GreaterEqual: '>=';

AndAnd: '&&' | 'and';

OrOr: '||' | 'or';

PlusPlus: '++';

MinusMinus: '--';

Comma: ',';

ArrowStar: '->*';

Arrow: '->';

Question: '?';

Colon: ':';

Doublecolon: '::';

Semi: ';';

Dot: '.';

DotStar: '.*';

Ellipsis: '...';

// boolean literal

BooleanLiteral: False_ | True_;

// sign
fragment Sign: [+-];

// Dights of different radix
fragment DecimalDigit: [0-9];

fragment NonZeroDecimalDigit: [0-9];

fragment BinaryDight: [0-1];

fragment OctalDight: [0-7];

fragment HexadecimalDight: [0-9a-fA-F];

fragment Unsignedsuffix: [uU];

fragment Longsuffix: [lL];

fragment Longlongsuffix: 'll' | 'LL';

Integersuffix:
	Unsignedsuffix Longsuffix?
	| Unsignedsuffix Longlongsuffix?
	| Longsuffix Unsignedsuffix?
	| Longlongsuffix Unsignedsuffix?;

// \' for digits like 1'000'000

DecimalLiteral: NonZeroDecimalDigit ('\''? DecimalDigit)*;

OctalLiteral: '0' ('\''? OctalDight)*;

HexadecimalLiteral: ('0x' | '0X') HexadecimalDight ( '\''? HexadecimalDight)*;

BinaryLiteral: ('0b' | '0B') BinaryDight ('\''? BinaryDight)*;

IntegerLiteral: Sign? (DecimalLiteral | OctalLiteral  | HexadecimalLiteral | BinaryLiteral) IntegerLiteral?;


// float litercal

fragment DigitSequence: DecimalDigit ('\''? DecimalDigit)*;

fragment NonZeroStartedDigitSequence: NonZeroDecimalDigit ('\''? DecimalDigit);

fragment Fractionalconstant: NonZeroDecimalDigit '.' DigitSequence | DigitSequence '.' | '0'? '.' DigitSequence;

fragment Exponentpart: ('e' | 'E') Sign? DigitSequence;

fragment Floatingsuffix: [flFL];

FloatingLiteral:
	Fractionalconstant Exponentpart? Floatingsuffix?
	| DigitSequence Exponentpart Floatingsuffix?;

// character literal

fragment CharCharacter: ~ ['\\] | SimpleEscapeCharacter ;

CharacterLiteral: '\'' CharCharacter+ '\'';

// string litercal

fragment NONDIGIT:[a-zA-Z_];

fragment RawString: 'R"''"';

fragment StringCharacter: ~ ["\\] | SimpleEscapeCharacter ;

fragment StandardString: '"' StringCharacter* '"';

fragment SimpleEscapeCharacter:
	'\\\''
	| '\\"'
	| '\\?'
	| '\\\\'
	| '\\a'
	| '\\b'
	| '\\f'
	| '\\n'
	| '\\r'
	| ('\\' ('\r' '\n'? | '\n'))
	| '\\t'
	| '\\v';

StringLiteral: (RawString | StandardString);


// Literals to skip
Whitespace: [ \t]+ -> skip;

Newline: ('\r' '\n'? | '\n') -> skip;

BlockComment: '/*' .*? '*/' -> skip;

LineComment: '//' ~ [\r\n]* -> skip;