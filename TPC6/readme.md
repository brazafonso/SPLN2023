# **TPC 6**

## Scraping de noticias
Continuar o trabalho da última aula, isto é, scraping de um site de notícias (JN neste caso) utilizando o pacote newspaper3k.  
Em geral o scraping manteu-se semelhante, tornando apenas mais arranjado o formato xml e acrescentando logs e prints para manter o utilizador informado sobre o decorrer do programa.  

## Guardar noticias e tornar programa numa tarefa automática periódica
A segunda parte do trabalho consistiu em criar um conjunto de pastas de forma a organizar as noticias obtidas. Isto consegui-se com o programa a verificar a data da recolha, e colocando na pasta do mês dentro da pasta do ano desta data, no ficheiro com o número do dia as notícias (*create_date_dirs*), em modo *'a'* para o caso de serem feitas múltiplas recolhas diáriamente.  
De forma a tornar o programa periódico, usou-se a ferramenta do unix **cron**, seguindo os seguintes comandos.

* Abrir editor de tarefas automáticas : crontab -e
* Inserir nova tarefa :  
0 5 * * * python3 '<path>/JN-corpus.py' - significando que às 5 da manhã todos os dias a aplicação será corrida

