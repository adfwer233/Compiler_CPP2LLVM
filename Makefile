build: grammar/SimpleCpp.g4
	antlr4 -Dlanguage=Python3 grammar/SimpleCpp.g4 -visitor -o src

clean:
	-rm -rf src