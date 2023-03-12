# **TPC3**


## Gramática e lexer
Primeiramente foram feitas correções no lexer e parser da gramática do dicionário simplificado criado na aula de modo a conseguir corretamente reconhecer todas as entidades no *dicionario_global_medicina.txt*.
### Ficheiros :
  - dicmed_lex.py : lexer
  - dicmed_sem.py : parser sintático e semântico
  - dicionario_global_medicina.txt : valores do dicionário guardados no formato da gramática


## Estrutura de dados intermédia
Com o parser sintático funcional, passamos a dar-lhe valor semântico e com este, é criada uma estrutura de dados para guardar a informação reconhecida num dicionário python, que é posteriormente guardado em *entries_dic* com o uso da bibilioteca pickle.
### Ficheiros :
  - dicmed_sem.py : parser sintático e semântica para criação da estrutura de dados
  - entries_dic : estrutura de dados serializada

## Criação de uma nova visão
Com o uso da estrutura de dados criada, é feita uma nova visão para estes dados. A visão escolhida foi em formato html, onde é criada uma página com um índice com todas as entradas que ligam diretamente para a entrada extensa, que revela mais informação sobre a mesma.
### Ficheiros :
  - entries_dic : estrutura de dados serializada
  - create_dicionario_html.py : script para a criação da visão html
  - dicionario.html : visão resultante