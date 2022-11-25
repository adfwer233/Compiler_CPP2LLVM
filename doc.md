## 配置环境

```bash
pip install -r requirements.txt
```

执行 `antlr`，选 yes

## 生成 lexer 和 parser

作为例子，我们生成一个 CPP14 的 lexer 和 parser

从这里下载语法文件

[CPP14 g4 files](https://github.com/antlr/grammars-v4/tree/master/cpp)

```
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Lexer.g4
wget https://raw.githubusercontent.com/antlr/grammars-v4/master/cpp/CPP14Parser.g4
```

然后通过 g4 语法文件生成 lexer 和 parser

```bash
antlr4 -Dlanguage=Python3 CPP14Lexer.g4 CPP14Parser.g4
```

然后会生成一堆文件，其中的 `CPP14Lexer.py` 和 `CPP14Parser.py` 就是Lexer 和 Parser，我们可以直接使用它们

## 使用 Lexer 和 Parser

我们在 example 中创建一个 main.py，执行 
```bash
python main.py test.cpp
```
即可生成语法树