# **TPC2**

## Dicionário de medicina geral
Para isto foi criado o script *general-dic.py* que percorre o dicionário anteriormente criado (galego) e, considerando as entradas remissivas dispensáveis (por apenas serem redirecionamentos de variações de termos), é escolhido um termo geral para cada entrada, neste caso o inglês por ser a língua universal, e o galego é considerado como qualquer outra das traduções. Assim os sinónimos e variações acompanham o termo em galego para dentro da lista de linguagens. \
Esta lista é ainda modificada para quando existem mais do que um termo para uma linguagem, todos à exceção do primeiro são considerados sinónimos. \
Ficamos então com um dicionário do tipo:
- Termo universal
- Areas
  [area1,area2...]
- Traducoes
  [lingua1 : \
    {\
      termo\
      sinonimos?
        [sin1,sin2...]\
      variacoes?
        [var1,var2...]\
    }\
  ]
---
Que é guardado no ficheiro *global_medicina_resultado.json*. \
Algumas correções foram também feitas no TPC1 para corrigir algumas das entradas e apanhar alguams casos especiais. O dicionário galego, resultante do TPC1, foi escrito no ficheiro *medicina_galego_resultado.json*.

*medicina_processado.txt* : resultado da marcacao do ficheiro xml do dicionario

## Gramática e lexer

Para a segunda parte tinhamos de, para a gramática acordada durante a aula (*dicmed_lex.py*), criar um lexer capaz de reconhecer os símbolos definidos (dicmed_sem.py).
