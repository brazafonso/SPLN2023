import sys
import time

def contar_palavras(nome_arquivo):
    try:
        with open(nome_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            palavras = conteudo.split()
            return len(palavras)
    except FileNotFoundError:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado.")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Por favor, forneça o nome do arquivo como argumento.")
    else:
        nome_arquivo = sys.argv[1]
        numero_palavras = contar_palavras(nome_arquivo)
        time.sleep(10)
        print(f"O arquivo '{nome_arquivo}' contém {numero_palavras} palavras.")
