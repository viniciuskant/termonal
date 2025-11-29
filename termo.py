import os
import random
import argparse
from itertools import product
import math

VERDE = '\033[92m'
AMARELO = '\033[95m'
BRANCO = '\033[97m'
CINZA = '\033[30m'
RESET = '\033[0m'


def init_estado_letras(dicionario):
    for i in range(ord('a'), ord('z') + 1):
        letra = chr(i)
        dicionario[letra] = "branco"

def simplifica(palavra):
    inversoes = {
        'à': 'a', 'á': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'è': 'e', 'é': 'e', 'ẽ': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'ĩ': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'ũ': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }
    palavra = [inversoes.get(i, i) for i in palavra]
    return "".join(palavra)

def ler_palavras(diretorio, tamanho):
    palavras = {}
    peso = []
    conjugacoes = set()
    path_conj = 'pt-br/conjugações'
    path_icf = 'pt-br/icf'

    with open(os.path.join(path_conj), 'r', encoding='utf-8') as f:
        for linha in f.readlines():
            palavra = linha.strip().lower()
            if len(palavra) != tamanho:
                continue
            conjugacoes.add(palavra)

    with open(os.path.join(path_icf), 'r', encoding='utf-8') as f:
        for linha in f.readlines():
            linha = linha.split(",")
            tupla = (linha[0], float(linha[1][:-1]))

            if tupla[0] in conjugacoes:
                continue
            if len(tupla[0]) != tamanho:
                continue

            simplificada = simplifica(tupla[0])

            if simplificada not in palavras:
                palavras[simplificada] = tupla[0]
                peso.append(tupla)

    return palavras, peso

def dar_feedback(palavra, tentativa):
    palavra = simplifica(palavra)
    tentativa_original = tentativa
    tentativa = simplifica(tentativa)
    
    feedback = []
    letras_verificadas = []
    resultado = []
    
    for i in range(len(palavra)):
        if tentativa[i] == palavra[i]:
            feedback.append('verde')
            letras_verificadas.append(tentativa[i])
            resultado.append(f"{VERDE}{tentativa_original[i].upper()}{RESET}")
        else:
            feedback.append(None)
            resultado.append(None)
    
    for i in range(len(palavra)):
        if feedback[i] == 'verde':
            continue 
        
        if tentativa[i] in palavra:
            total_na_palavra = palavra.count(tentativa[i])
            ja_marcadas = letras_verificadas.count(tentativa[i])
            
            if ja_marcadas < total_na_palavra:
                feedback[i] = 'amarelo'
                resultado[i] = f"{AMARELO}{tentativa_original[i].upper()}{RESET}"
                letras_verificadas.append(tentativa[i])
            else:
                feedback[i] = 'cinza'
                resultado[i] = f"{BRANCO}{tentativa_original[i].upper()}{RESET}"
        else:
            feedback[i] = 'cinza'
            resultado[i] = f"{BRANCO}{tentativa_original[i].upper()}{RESET}"
    
    return ' '.join(resultado), feedback, tentativa_original

def atualizar_estado_letras(estado, feedback, tentativa):
    """
    Atualiza o estado das letras baseado no feedback da tentativa atual
    """
    tentativa_simplificada = simplifica(tentativa)
    
    for i, letra in enumerate(tentativa_simplificada):
        if estado[letra] == "verde":
            continue
        if estado[letra] == "amarelo" and feedback[i] != "verde":
            continue
        estado[letra] = feedback[i]
        
def print_estado_letras(estado):
    string_formatada = []
    cores = {"verde": VERDE, "amarelo": AMARELO, "cinza": CINZA, "branco": BRANCO}

    for letra, cor in estado.items():
        string_formatada.append(f"{cores[cor]}{letra.upper()}{RESET}")

    return ' '.join(string_formatada)

def clear_line():
    """Apaga a linha atual no terminal"""
    print('\033[2K', end='\r')

def probs_exponencial(pesos, alpha=1.0):
    palavras, w = zip(*pesos)
    scores = [math.exp(-alpha * x) for x in w] 
    soma = sum(scores)
    probs = [s / soma for s in scores]
    return list(palavras), probs


def jogar(palavras, pesos, tentativas_max):
    escolha, probs = probs_exponencial(pesos)
    palavra_correta = random.choices(escolha, weights=probs, k=1)[0]


    tentativas = 0
    estado_letras = {}
    init_estado_letras(estado_letras)
    historico_tentativas = []

    print("\n" + "="*50)
    print("LEGENDA DE CORES:")
    print(f"{VERDE}VERDE{RESET}: Letra na posição CORRETA")
    print(f"{AMARELO}ROSA{RESET}: Letra existe na palavra mas em OUTRA posição")
    print(f"{BRANCO}BRANCO{RESET}: Letra NÃO existe na palavra")
    print("="*50)
    print()

    while tentativas < tentativas_max:
        print_estado = print_estado_letras(estado_letras)
        print(f"Letras: {print_estado}")
        print()

        for i, (tentativa_str, feedback_str) in enumerate(historico_tentativas):
            print(f"Tentativa   {i+1}: {feedback_str}")
        
        
        try:
            tentativa = input(f"Tentativa {tentativas + 1}/{tentativas_max}: ").strip().lower()
            clear_line()
            
            for _ in range(3 + len(historico_tentativas)):
                print('\033[1A', end='') 
                print('\033[2K', end='') 
        except (EOFError, KeyboardInterrupt):
            print(f"\n\nSaindo... A palavra correta era: {VERDE}{palavra_correta.upper()}{RESET}")
            return

        if len(tentativa) != len(palavra_correta):
            print(f"A palavra deve ter {len(palavra_correta)} letras!")
            input("Pressione Enter para continuar...")
            clear_line()
            print('\033[1A\033[2K', end='')
            continue

        tentativa_norm = simplifica(tentativa)

        if tentativa_norm not in palavras:
            print(f"'{tentativa}' não é aceita!")
            input("Pressione Enter para continuar...")
            clear_line()
            print('\033[1A\033[2K', end='')
            continue

        tentativa = palavras[tentativa_norm]

        feedback_str, feedback_detalhado, tentativa_original = dar_feedback(palavra_correta, tentativa)
        
        historico_tentativas.append((tentativa_original, feedback_str))
        
        if tentativa == palavra_correta:
            for i, (tentativa_hist, feedback_hist) in enumerate(historico_tentativas):
                print(f"Tentativa {i+1}: {feedback_hist}")
            print_estado = print_estado_letras(estado_letras)
            print(f"Letras: {print_estado}")
            print("\nParabéns, você acertou a palavra!")
            break

        atualizar_estado_letras(estado_letras, feedback_detalhado, tentativa_original)
        tentativas += 1

    if tentativas >= tentativas_max and tentativa != palavra_correta:
        for i, (tentativa_hist, feedback_hist) in enumerate(historico_tentativas):
            print(f"Tentativa {i+1}: {feedback_hist}")
        print_estado = print_estado_letras(estado_letras)
        print(f"Letras: {print_estado}")
        print(f"\nVocê perdeu! A palavra correta era: {VERDE}{palavra_correta.upper()}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Jogo estilo Termo")
    parser.add_argument('tamanho', type=int, help="Número de letras da palavra")
    parser.add_argument('tentativas', type=int, help="Número de tentativas possíveis")
    args = parser.parse_args()
    
    diretorio = 'termo/pt-br'

    palavras, pesos = ler_palavras(diretorio, args.tamanho)

    if len(palavras) == 0:
        print(f"Não há palavras com {args.tamanho} letras no léxico.")
        return

    print(f"\nBem-vindo ao jogo Termo!")
    print(f"Você tem {args.tentativas} tentativas para acertar a palavra de {args.tamanho} letras.")
    jogar(palavras, pesos, args.tentativas)

if __name__ == "__main__":
    main()
