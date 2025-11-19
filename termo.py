import os
import random
import argparse

def simplifica(palavra):
    dicionario = {
        'a':'a', 'á':'a', 'ã':'a', 'â':'a', 'b':'b', 'c':'c', 'ç':'c', 'd':'d', 'e':'e', 'é':'e', 'ê':'e', 'f':'f', 'g':'g', 'h':'h', 'i':'i', 'í':'i', 'j':'j', 'k':'k', 'l':'l', 'm':'m', 'n':'n', 'o':'o', 'ó':'o', 'ô':'o', 'p':'p', 'q':'q', 'r':'r', 's':'s', 't':'t', 'u':'u', 'v':'v', 'w':'w', 'x':'x', 'y':'y', 'z':'z'
    }
    palavra = [dicionario[i] for i in palavra]
    palavra = "".join(palavra)

def ler_palavras(diretorio, tamanho):
    palavras = []
    path = 'pt-br/lexico'
    path = 'pt-br/icf'
    with open(os.path.join(path), 'r', encoding='utf-8') as f:
        for linha in f.readlines():
            linha = linha.split(",")[0]
            palavra = linha.strip().lower()
            if len(palavra) == tamanho:
                palavras.append(palavra)
    return palavras
    

def dar_feedback(palavra, tentativa):
    palavra = simplifica(palavra)
    tentativa = simplifica(palavra)

    VERDE = '\033[92m'  
    AMARELO = '\033[93m'  
    BRANCO = '\033[97m'   
    RESET = '\033[0m'    
    
    feedback = []
    letras_verificadas = []
    resultado = []
    
    for i in range(len(palavra)):
        if tentativa[i] == palavra[i]:
            feedback.append('verde')
            letras_verificadas.append(tentativa[i])
            resultado.append(f"{VERDE}{tentativa[i].upper()}{RESET}")
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
                resultado[i] = f"{AMARELO}{tentativa[i].upper()}{RESET}"
                letras_verificadas.append(tentativa[i])
            else:
                feedback[i] = 'branco'
                resultado[i] = f"{BRANCO}{tentativa[i].upper()}{RESET}"
        else:
            feedback[i] = 'branco'
            resultado[i] = f"{BRANCO}{tentativa[i].upper()}{RESET}"
    
    return ' '.join(resultado)


def jogar(palavras, tentativas_max):
    palavra_correta = random.choice(palavras)
    tentativas = 0
    
    
    print("\n" + "="*50)
    print("LEGENDA DE CORES:")
    print("\033[92mVERDE\033[0m: Letra na posição CORRETA")
    print("\033[93mAMARELO\033[0m: Letra existe na palavra mas em OUTRA posição")
    print("\033[97mBRANCO\033[0m: Letra NÃO existe na palavra")
    print("="*50)
    print()

    while tentativas < tentativas_max:
        tentativa = input(f"Tentativa {tentativas + 1}/{tentativas_max}: ").strip().lower()

        if len(tentativa) != len(palavra_correta):
            print(f"A palavra deve ter {len(palavra_correta)} letras!")
            continue

        if tentativa not in palavras:
            print("Essa palavra não é aceita!")
            continue

        if tentativa == palavra_correta:
            feedback = dar_feedback(palavra_correta, tentativa)
            print("Palavra:", feedback)
            print("\nParabéns, você acertou a palavra!")
            break

        feedback = dar_feedback(palavra_correta, tentativa)
        print("Palavra:", feedback)
        print()  
        tentativas += 1

    if tentativas >= tentativas_max and tentativa != palavra_correta:
        print(f"\nVocê perdeu! A palavra correta era: {palavra_correta.upper()}")

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
