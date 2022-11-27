lexer: grammar/MyCPPLexer.g4
	antlr4 -Dlanguage=Python3 grammar/MyCPPLexer.g4 -o src

clean:
	-rm -rf src