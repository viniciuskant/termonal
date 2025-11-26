import os
import random
import argparse
from itertools import product
 
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
    dicionario = {
        'a':'a', 'á':'a', 'ã':'a', 'â':'a', 'b':'b', 'c':'c', 'ç':'c', 'd':'d', 'e':'e', 'é':'e', 'ê':'e', 'f':'f', 'g':'g', 'h':'h', 'i':'i', 'í':'i', 'j':'j', 'k':'k', 'l':'l', 'm':'m', 'n':'n', 'o':'o', 'ó':'o', 'ô':'o', 'p':'p', 'q':'q', 'r':'r', 's':'s', 't':'t', 'u':'u', 'ú':'u', 'ü':'u', 'v':'v', 'w':'w', 'x':'x', 'y':'y', 'z':'z'
    }
    palavra = [dicionario[i] for i in palavra]
    return "".join(palavra)

def possibilidades(palavra, palavras):
    dicionario = {
        'a': ['a', 'á', 'ã', 'â'],
        'c': ['c', 'ç'],
        'e': ['e', 'é', 'ê'],
        'i': ['i', 'í'],
        'o': ['o', 'ó', 'ô'],
        'u': ['u', 'ú', 'ü']
    }
    
    inversoes = {
        'á': 'a', 'ã': 'a', 'â': 'a', 'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o', 'ô': 'o', 'ú': 'u', 'ü': 'u', 'ç': 'c'
    }
    
    variacoes = []
    for letra in palavra:
        if letra in dicionario:
            variacoes.append(dicionario[letra])
        else:
            if letra in inversoes:
                letra_base = inversoes[letra]
                if letra_base in dicionario:
                    variacoes.append(dicionario[letra_base])
                else:
                    variacoes.append([letra])
            else:
                variacoes.append([letra])

    possibilidades_palavras = [''.join(comb) for comb in product(*variacoes)]
    
    retorno = [p for p in possibilidades_palavras if p in palavras]
    
    return retorno

def ler_palavras(diretorio, tamanho):
    palavras = []
    conjugacoes = []
    path_conj = 'pt-br/conjugações'
    path_icf = 'pt-br/icf'

    with open(os.path.join(path_conj), 'r', encoding='utf-8') as f:
        for linha in f.readlines():
            palavra = linha.strip().lower()
            if len(palavra) == tamanho:
                conjugacoes.append(palavra)

    with open(os.path.join(path_icf), 'r', encoding='utf-8') as f:
        for linha in f.readlines():
            linha = linha.split(",")[0]
            palavra = linha.strip().lower()

            if len(palavra) == tamanho and palavra not in conjugacoes:
                palavras.append(palavra)

    return palavras

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

def jogar(palavras, tentativas_max):
    palavra_correta = random.choice(palavras)
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

        possiveis_tentativas = possibilidades(tentativa, palavras)

        if len(possiveis_tentativas) == 0:
            print("Essa palavra não é aceita!")
            input("Pressione Enter para continuar...")
            clear_line()
            print('\033[1A\033[2K', end='')
            continue

        if palavra_correta in possiveis_tentativas:
            tentativa = palavra_correta
        elif tentativa not in possiveis_tentativas:
            tentativa = possiveis_tentativas[0]

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

    palavras = ler_palavras(diretorio, args.tamanho)

    if len(palavras) == 0:
        print(f"Não há palavras com {args.tamanho} letras no léxico.")
        return

    print(f"\nBem-vindo ao jogo Termo!")
    print(f"Você tem {args.tentativas} tentativas para acertar a palavra de {args.tamanho} letras.")
    jogar(palavras, args.tentativas)

if __name__ == "__main__":
    main()