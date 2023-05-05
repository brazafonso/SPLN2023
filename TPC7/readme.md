**TPC 6**

## Objetivo
Utilizando W2V word embedding e como corpus as noticías conseguidas no TPC6, criar um modelo de machine learning capaz de entender similaridades entre palavras conhecidas desse corpus.  
Criar um conjunto de relações para verificar resultados.


## Corpus
O corpus vem dos resultados do tpc anterior, que pode ser corrido diariamente para conseguir artigos mais recentes. A script criada é no entanto mais genérica podendo ser dada uma pasta como diretoria do corpus, onde serão procurados todos os ficheiros html e txt, sendo que a diferença na extração de informação será que nos html apenas se procurará o texto em tags *text* (usando BeautifulSoup).

## Modelo
A construção do modelo segue o fluxo do construído na aula, sendo este construído usando Word2Vec com o corpus anterior. Este modelo pode ser guardado, carregado e treinado novamente de acordo com as flags dadas nos argumentos.

## Relações
Se for dado um ficheiro onde se possa ler pedidos de cálculo de relações, este será lido linha a linha de forma a detetar um de 3 tipos: analogia, por exemplo **portugal europa brasil** onde se procura encontrar as palavras com relaçõe com brasil semelhante à de europa para portugal; mais semelhantes, por exemplo **futebol**, procurando as palavras mais relacionadas com futebol; e similaridade entre duas palavras, por exemplo **água bom|mau** onde se procura calcular se água está mais próximo de bom ou de mau.

## Opções
    --------------------------------------------------------------------
                                **W2V model**
    --------------------------------------------------------------------

    optional arguments:
    -h, --help            show this help message and exit
    -d DIRECTORY, --directory DIRECTORY
                            folder with the corpus files
    -e EPOCHS, --epochs EPOCHS
                            number of epochs to train the model
    -dim DIMENSION, --dimension DIMENSION
                            dimension of the word vectors to create
    -s SAVE, --save SAVE  file to save the model
    -lm LOAD_MODEL, --load_model LOAD_MODEL
                            file from where to load model
    -t, --train           option to chose whether to continue training model
    -q QUERIES, --queries QUERIES
                            file with queries to test
