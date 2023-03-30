# **TPC1**

script: *vocabulario-medicina.py*

## Marcar xml
Após entender o objetivo do trabalho e do dicionário com que estamos a trabalhar, passamos então a tratar de identificar os seus elementos no seu xml correspondente. \
Começamos por retirar o header e o footer das páginas para diminuir a quantidade de blocos. Seguimos por marcar as entradas, que são os itens principais, começando pelas completas que contêm informação como numeração que as distingue das outras, as remissivas. \
Os diferentes atributos são então tratados separadamente de acordo com as suas individualidades no xml, como tamanho de fonte específico por exemplo, tentando incluír ainda alguns outliers que não cumprem estas regras \
O resultado desta marcação é guardado no ficheiro *medicina_processado.txt*.

## Processar xml marcado

Com o resultado da marcação, foi adicionado açúcar sintático suficiente para facilmente partir o texto em diferentes entradas e coletar os seus diferentes atributos com o uso de apenas splits e expressões regulares, embora o mesmo pude-se ser concretizado com o uso de uma gramática. \
O resultado deste processamento é um dicionário com todas as entradas que não deram erro no processamento (apenas 21 deram erro de cerca de 8000), que será guardado em formato de json (*medicina_galego_resultado.json*), separando as entradas completas e as remissivas. Este mantém o mesmo contexto do ficheiro original, continuando a ser um dicionário galego.
