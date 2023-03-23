# **TPC 5**

Continuar a acrescentar funcionalidades ao tokenizer, para além de o tornar instalável utilizando o *flint*.  
Correções de bugs como deteção de capítulos se tiverem uma linha em branco a separar o texto e não separar palavras com hífens.  
Adpatação do parser de argumentos para utilizar o *argparser*.  
Funcionalidades (tok -h):  

    usage: tok [-h] [-o OUTPUT] [-lan LANGUAGE] [-p] [-c [OPTIONS]] [-pu] [-pb] [-js] [-spl] [-par] [--version] [filename]

    --------------------------------------------------------------------
                    **Tokenizer SPLN version 0.5**
    --------------------------------------------------------------------
                Module to tokenize books (English by default)

    positional arguments:
      filename              input file of the text to tokenize

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            defines an output file
      -lan LANGUAGE, --language LANGUAGE
                            defines a language to recognize, accordingly will use the languages settings (abreviatures,
                            delimiters) (default to english)
      -p, --poem            saves poems delimited inside <poem></poem> in the text
      -c, --chapter         treat chapters using the language delimiters (default english)
      -pu, --punctuation    treat punctuation using the language abreviations (default english)
      -pb, --pagebreak      treat pagebreak
      -js, --JoinSentence   treat sentences broken between lines, bringing them to the same line
      -spl, --SentencePerLine
                            each sentence is seperated to an individual line
      -par, --paragraphs    treat paragraphs, delimiting them with /PAR/
      --version, -V         show program's version number and exit

Ficheiros de configuração na pasta *conf* para guardar abreviaturas e capítulos, separadamente, e em várias línguas.  
Linguagem default é inglês.