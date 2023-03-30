# **TPC4**


## Tokenizer
Utilizando como base o tokenizer criado na aula, este foi completado de acordo com as 6 funcionalidades definidas : 
  - Quebra de pagina
  - Separar pontuação das palavras
  - Marcar capitulos
  - Separar paragrafos de linhas pequenas
  - Juntar linhas da mesma frase
  - Uma frase por linha
  - Tratar Poemas (tagged)
  
Além de implementar estas funcionalidades, opções extra foram adicionadas ao programa, tal como definir o ficheiro de input, output, ou se é para se tratar de poemas. 

Para isto foram criadas um conjunto de funções para servir de parser dos argumentos. 
Seguindo os seguintes passos[**[source](https://dbader.org/blog/how-to-make-command-line-commands-with-python)**  ], o programa foi tornado num comando shell (tokenizerspln):
  - chmod +x tokenizerspln.py -> marca script como executavel
  - adicionar '#! /usr/bin/env python3' na script -> define interpretador do executavel
  - mv tokenizerspln.py tokenizerspln -> simplificar chamada do executavel
  - mkdir -p ~/bin -> criar diretorio bin
  - cp TP4 ~/bin -> copiar a pasta do projeto para bin
  - (dentro de ~/bin) mv TP4 tokenizerSPLN -> mudar nome do projeto no bin
  - export PATH=$PATH":$HOME/bin/tokenizerSPLN" -> adicionar projeto (no bin) ao path
  - (dentro de $HOME) echo 'export PATH=$PATH":$HOME/bin"' >> .profile -> torna o comando disponivel mesmo após restart


Por último, foi criada uma script para atualizar o programa no comando shell criado.
### Ficheiros :
  - tokenizerspln.py : tokenizer
  - utils.py : conjunto de funções auxiliares para parsing dos argumentos
  - update_bash_command.sh : script para atualizar comando de shell tokenizer com atualizações feitas no projeto

