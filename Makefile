lexer: grammar/cppLexer.g4
	antlr4 -Dlanguage=Python3 grammar/cppLexer.g4 -visitor -o src

clean:
	-rm -rf src