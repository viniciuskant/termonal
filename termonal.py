import os
import random
import argparse
import math
from collections import defaultdict

# Códigos de cores para terminal
VERDE = '\033[92m'
AMARELO = '\033[95m'
BRANCO = '\033[97m'
CINZA = '\033[30m'
RESET = '\033[0m'

# Cores para identificar diferentes palavras
CORES_PALAVRAS = ['\033[93m', '\033[96m', '\033[91m', '\033[94m']  # Amarelo, Ciano, Vermelho, Azul


def inicializar_estado_letras(estado_letras):
    for codigo in range(ord('a'), ord('z') + 1):
        letra = chr(codigo)
        estado_letras[letra] = "branco"


def inicializar_estados_multiplos(modo_jogo):
    estados = []
    for _ in range(modo_jogo):
        estado = {}
        inicializar_estado_letras(estado)
        estados.append(estado)
    return estados


def normalizar_palavra(palavra):
    mapa_normalizacao = {
        'à': 'a', 'á': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'è': 'e', 'é': 'e', 'ẽ': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'ĩ': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'ũ': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }
    caracteres_normalizados = [mapa_normalizacao.get(caractere, caractere) for caractere in palavra]
    return "".join(caracteres_normalizados)


def carregar_palavras(tamanho_palavra):
    dicionario_normalizado = {}
    dicionario_equivalentes = {}
    lista_pesos = []
    caminho_arquivo = 'pt-br/icf'
    
    with open(os.path.join(caminho_arquivo), 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()

    linha_atual = 0
    while linha_atual < len(linhas):
        partes_linha = linhas[linha_atual].strip().split(",")
        entrada = (partes_linha[0], float(partes_linha[1]))

        if len(entrada[0]) != tamanho_palavra:
            linha_atual += 1
            continue

        palavra_sem_acentos = normalizar_palavra(entrada[0])

        variantes = [entrada[0]]
        deslocamento = 1

        while linha_atual + deslocamento < len(linhas):
            linha_variante = linhas[linha_atual + deslocamento].strip().split(",")
            entrada_variante = (linha_variante[0], float(linha_variante[1]))
            palavra_variante_sem_acentos = normalizar_palavra(entrada_variante[0])

            if palavra_sem_acentos != palavra_variante_sem_acentos:
                break

            variantes.append(entrada_variante[0])
            deslocamento += 1

        dicionario_equivalentes[palavra_sem_acentos] = variantes

        if palavra_sem_acentos not in dicionario_normalizado:
            dicionario_normalizado[palavra_sem_acentos] = entrada[0]
            lista_pesos.append(entrada)

        linha_atual += deslocamento

    return dicionario_normalizado, lista_pesos, dicionario_equivalentes


def calcular_feedback(palavra_secreta, tentativa_usuario):
    palavra_secreta_normalizada = normalizar_palavra(palavra_secreta)
    tentativa_original = tentativa_usuario
    tentativa_normalizada = normalizar_palavra(tentativa_usuario)
    
    feedback = []
    letras_processadas = []
    resultado_formatado = []
    
    for posicao in range(len(palavra_secreta)):
        if tentativa_normalizada[posicao] == palavra_secreta_normalizada[posicao]:
            feedback.append('verde')
            letras_processadas.append(tentativa_normalizada[posicao])
            resultado_formatado.append(f"{VERDE}{tentativa_original[posicao].upper()}{RESET}")
        else:
            feedback.append(None)
            resultado_formatado.append(None)
    
    for posicao in range(len(palavra_secreta)):
        if feedback[posicao] == 'verde':
            continue 
        
        letra_tentativa = tentativa_normalizada[posicao]
        
        if letra_tentativa in palavra_secreta_normalizada:
            quantidade_na_palavra = palavra_secreta_normalizada.count(letra_tentativa)
            quantidade_marcada = letras_processadas.count(letra_tentativa)
            
            if quantidade_marcada < quantidade_na_palavra:
                feedback[posicao] = 'amarelo'
                resultado_formatado[posicao] = f"{AMARELO}{tentativa_original[posicao].upper()}{RESET}"
                letras_processadas.append(letra_tentativa)
            else:
                feedback[posicao] = 'cinza'
                resultado_formatado[posicao] = f"{BRANCO}{tentativa_original[posicao].upper()}{RESET}"
        else:
            feedback[posicao] = 'cinza'
            resultado_formatado[posicao] = f"{BRANCO}{tentativa_original[posicao].upper()}{RESET}"
    
    return ' '.join(resultado_formatado), feedback, tentativa_original


def calcular_feedback_multiplas_palavras(palavras_secretas, tentativa_usuario):
    resultados = []
    
    for idx, palavra_secreta in enumerate(palavras_secretas):
        feedback_str, feedback_detalhado, tentativa_original = calcular_feedback(palavra_secreta, tentativa_usuario)
        
        # Verifica se acertou esta palavra
        palavra_normalizada = normalizar_palavra(palavra_secreta)
        tentativa_normalizada = normalizar_palavra(tentativa_usuario)
        acertou = (tentativa_normalizada == palavra_normalizada)
        
        resultados.append((feedback_str, feedback_detalhado, acertou, tentativa_original))
    
    return resultados


def atualizar_estado_letras(estado_letras, feedback, tentativa):
    tentativa_normalizada = normalizar_palavra(tentativa)
    
    for posicao, letra in enumerate(tentativa_normalizada):
        estado_atual = estado_letras[letra]
        
        if estado_atual == "verde":
            continue
            
        if estado_atual == "amarelo" and feedback[posicao] != "verde":
            continue
            
        estado_letras[letra] = feedback[posicao]


def formatar_estado_letras(estado_letras, cor_prefixo=None):
    letras_formatadas = []
    codigos_cores = {"verde": VERDE, "amarelo": AMARELO, "cinza": CINZA, "branco": BRANCO}

    for letra, estado in estado_letras.items():
        letras_formatadas.append(f"{codigos_cores[estado]}{letra.upper()}{RESET}")

    letras_str = ' '.join(letras_formatadas)
    
    if cor_prefixo:
        return f"{cor_prefixo}{letras_str}{RESET}"
    return letras_str


def limpar_linha():
    print('\033[2K', end='\r')


def calcular_probabilidades_exponenciais(lista_pesos, fator_alpha=1.0):
    palavras_originais, pesos = zip(*lista_pesos)
    scores = [math.exp(-fator_alpha * peso) for peso in pesos]
    soma_scores = sum(scores)
    probabilidades = [score / soma_scores for score in scores]
    return list(palavras_originais), probabilidades


def selecionar_palavras_unicas(palavras_validas, probabilidades, quantidade):
    palavras_selecionadas = []
    palavras_ja_usadas = set()
    
    palavras_lista = palavras_validas.copy()
    prob_lista = probabilidades.copy()
    
    while len(palavras_selecionadas) < quantidade and palavras_lista:
        palavra_escolhida = random.choices(palavras_lista, weights=prob_lista, k=1)[0]
        
        if palavra_escolhida not in palavras_ja_usadas:
            palavras_selecionadas.append(palavra_escolhida)
            palavras_ja_usadas.add(palavra_escolhida)
        
        idx = palavras_lista.index(palavra_escolhida)
        palavras_lista.pop(idx)
        prob_lista.pop(idx)
        
        if prob_lista:
            soma = sum(prob_lista)
            prob_lista = [p/soma for p in prob_lista]
    
    return palavras_selecionadas


def exibir_quadro_multiplas_palavras(historico_tentativas, palavras_restantes, modo_jogo, cores_palavras, mascara, tamanho_palavra):
    print("\n" + "=" * (2 * (tamanho_palavra + 2) * modo_jogo + 11))
    print(f"Palavras restantes: {palavras_restantes}")
    print()

    max_tentativas = max(len(h) for h in historico_tentativas) if historico_tentativas else 0
    for tentativa_idx in range(max_tentativas):
        linha = f"Tentativa {tentativa_idx + 1}: "
        
        for palavra_idx in range(modo_jogo):
            if tentativa_idx < len(historico_tentativas[palavra_idx]) and tentativa_idx < mascara[palavra_idx]:
                feedback_str = historico_tentativas[palavra_idx][tentativa_idx][1]
                linha += f"  {cores_palavras[palavra_idx]}█{RESET} {feedback_str}"
            else:
                linha += f"  {cores_palavras[palavra_idx]}█{RESET}  {'  ' * (tamanho_palavra - 1)}"
        
        print(linha)
    
    print("=" * (2 * (tamanho_palavra + 2) * modo_jogo + 11))



def exibir_estados_letras_multiplos(estados_letras, modo_jogo, cores_palavras):
    for palavra_idx in range(modo_jogo):
        cor_prefixo = cores_palavras[palavra_idx]
        letras_formatadas = formatar_estado_letras(estados_letras[palavra_idx])
        print(f"{cor_prefixo}█ Palavra {palavra_idx + 1}:{RESET} {letras_formatadas}")
    print()


def executar_jogo_modo_unico(dicionario_palavras, lista_pesos, max_tentativas, dicionario_equivalentes):
    palavras_validas, probabilidades = calcular_probabilidades_exponenciais(lista_pesos)
    palavra_secreta = random.choices(palavras_validas, weights=probabilidades, k=1)[0]
    palavra_secreta_normalizada = normalizar_palavra(palavra_secreta)
    
    tentativas_realizadas = 0
    estado_letras = {}
    inicializar_estado_letras(estado_letras)
    historico_tentativas = []

    print("\n" + "="*50)
    print("LEGENDA DE CORES:")
    print(f"{VERDE}VERDE{RESET}: Letra na posição CORRETA")
    print(f"{AMARELO}ROSA{RESET}: Letra existe na palavra mas em OUTRA posição")
    print(f"{BRANCO}BRANCO{RESET}: Letra NÃO existe na palavra")
    print("="*50)
    print()

    while tentativas_realizadas < max_tentativas:
        estado_formatado = formatar_estado_letras(estado_letras)
        print(f"Letras: {estado_formatado}")
        print()

        for i, (tentativa_str, feedback_str) in enumerate(historico_tentativas):
            print(f"Tentativa   {i+1}: {feedback_str}")
        
        try:
            tentativa_usuario = input(f"Tentativa {tentativas_realizadas + 1}/{max_tentativas}: ").strip().lower()
            limpar_linha()
            
            for _ in range(3 + len(historico_tentativas)):
                print('\033[1A', end='') 
                print('\033[2K', end='') 
        except (EOFError, KeyboardInterrupt):
            print(f"\n\nSaindo... A palavra correta era: {VERDE}{palavra_secreta.upper()}{RESET}")
            return

        if len(tentativa_usuario) != len(palavra_secreta):
            print(f"A palavra deve ter {len(palavra_secreta)} letras!")
            input("Pressione Enter para continuar...")
            
            print('\033[1A\033[2K', end='')
            print('\033[1A\033[2K', end='')
            continue

        tentativa_normalizada = normalizar_palavra(tentativa_usuario)
        
        if tentativa_normalizada not in dicionario_palavras:
            print(f"{tentativa_usuario.upper()} não é aceita!")
            input("Pressione Enter para continuar...")
            limpar_linha()
            print('\033[1A\033[2K', end='')
            continue

        if tentativa_usuario in dicionario_equivalentes[tentativa_normalizada]:
            tentativa_usuario = tentativa_usuario
        else:
            tentativa_usuario = dicionario_equivalentes[tentativa_normalizada][0]

        feedback_formatado, feedback_detalhado, tentativa_processada = calcular_feedback(palavra_secreta, tentativa_usuario)
        
        historico_tentativas.append((tentativa_processada, feedback_formatado))
        
        if tentativa_normalizada == palavra_secreta_normalizada:
            for i, (tentativa_hist, feedback_hist) in enumerate(historico_tentativas):
                print(f"Tentativa {i+1}: {feedback_hist}")
            print("\nParabéns, você acertou a palavra!")
            break

        atualizar_estado_letras(estado_letras, feedback_detalhado, tentativa_processada)
        tentativas_realizadas += 1

    if tentativas_realizadas >= max_tentativas and tentativa_usuario != palavra_secreta:
        for i, (tentativa_hist, feedback_hist) in enumerate(historico_tentativas):
            print(f"Tentativa {i+1}: {feedback_hist}")
        print(f"\nVocê perdeu! A palavra correta era: {VERDE}{palavra_secreta.upper()}{RESET}")


def executar_jogo_modo_multiplo(dicionario_palavras, lista_pesos, max_tentativas, dicionario_equivalentes, modo_jogo):
    palavras_validas, probabilidades = calcular_probabilidades_exponenciais(lista_pesos)
    palavras_secretas = selecionar_palavras_unicas(palavras_validas, probabilidades, modo_jogo)

    if len(palavras_secretas) < modo_jogo:
        print(f"Não há palavras suficientes para jogar com {modo_jogo} palavras únicas.")
        return
    
    palavras_secretas_normalizadas = [normalizar_palavra(p) for p in palavras_secretas]
    
    tentativas_realizadas = 0
    estados_letras = inicializar_estados_multiplos(modo_jogo)
    
    historico_por_palavra = [[] for _ in range(modo_jogo)]
    
    palavras_acertadas = [False] * modo_jogo
    palavras_restantes = modo_jogo

    cores_palavras = CORES_PALAVRAS[:modo_jogo]

    print("\n" + "="*66)
    print(f"QUARTETO - Modo com {modo_jogo} palavras simultâneas")
    print("="*66)
    print("LEGENDA DE CORES:")
    print(f"{VERDE}VERDE{RESET}: Letra na posição CORRETA")
    print(f"{AMARELO}ROSA{RESET}: Letra existe na palavra mas em OUTRA posição")
    print(f"{BRANCO}BRANCO{RESET}: Letra NÃO existe na palavra")
    print("="*66)
    print()

    tamanho_palavra = len(palavras_secretas[0])
    mascara_acertos = [max_tentativas + 1] * 4

    while tentativas_realizadas < max_tentativas and palavras_restantes > 0:
        exibir_estados_letras_multiplos(estados_letras, modo_jogo, cores_palavras)
        
        exibir_quadro_multiplas_palavras(historico_por_palavra, palavras_restantes, modo_jogo, cores_palavras, mascara_acertos, tamanho_palavra)
        print()
        
        try:
            tentativa_usuario = input(f"Tentativa {tentativas_realizadas + 1}/{max_tentativas}: ").strip().lower()
            limpar_linha()
            
            linhas_exibidas = 3 + modo_jogo + 3 + max(len(h) for h in historico_por_palavra) + 2
            for _ in range(linhas_exibidas):
                print('\033[1A', end='') 
                print('\033[2K', end='') 
        except (EOFError, KeyboardInterrupt):
            print(f"\n\nSaindo... As palavras corretas eram:")
            for idx, palavra in enumerate(palavras_secretas):
                print(f"  {cores_palavras[idx]}█ Palavra {idx+1}: {VERDE}{palavra.upper()}{RESET}")
            return

        tamanho_palavra = len(palavras_secretas[0])
        if len(tentativa_usuario) != tamanho_palavra:
            print(f"A palavra deve ter {tamanho_palavra} letras!")
            input("Pressione Enter para continuar...")
            
            print('\033[1A\033[2K', end='')
            print('\033[1A\033[2K', end='')
            continue

        tentativa_normalizada = normalizar_palavra(tentativa_usuario)
        
        if tentativa_normalizada not in dicionario_palavras:
            print(f"{tentativa_usuario.upper()} não é aceita!")
            input("Pressione Enter para continuar...")
            limpar_linha()
            print('\033[1A\033[2K', end='')
            continue

        if tentativa_usuario in dicionario_equivalentes[tentativa_normalizada]:
            tentativa_usuario = tentativa_usuario
        else:
            tentativa_usuario = dicionario_equivalentes[tentativa_normalizada][0]

        resultados = calcular_feedback_multiplas_palavras(palavras_secretas, tentativa_usuario)
        
        for idx, (feedback_str, feedback_detalhado, acertou, tentativa_processada) in enumerate(resultados):
            historico_por_palavra[idx].append((tentativa_processada, feedback_str))
            
            if not palavras_acertadas[idx]:
                atualizar_estado_letras(estados_letras[idx], feedback_detalhado, tentativa_processada)
            
            if acertou and not palavras_acertadas[idx]:
                mascara_acertos[idx] = tentativas_realizadas + 1
                palavras_acertadas[idx] = True
                palavras_restantes -= 1

        tentativas_realizadas += 1

    print()
    exibir_quadro_multiplas_palavras(historico_por_palavra, palavras_restantes, modo_jogo, cores_palavras, mascara_acertos, tamanho_palavra)
    print()
    
    if palavras_restantes == 0:
        print(f"\nParabéns! Você acertou todas as {modo_jogo} palavras!")
    else:
        print(f"\nTentativas esgotadas! As palavras corretas eram:")
        for idx, palavra in enumerate(palavras_secretas):
            print(f" {cores_palavras[idx]}█ Palavra {idx+1}: {VERDE}{palavra.upper()}{RESET}")


def executar_jogo(dicionario_palavras, lista_pesos, max_tentativas, dicionario_equivalentes, modo_jogo=1):
    if modo_jogo == 1:
        executar_jogo_modo_unico(dicionario_palavras, lista_pesos, max_tentativas, dicionario_equivalentes)
    else:
        executar_jogo_modo_multiplo(dicionario_palavras, lista_pesos, max_tentativas, dicionario_equivalentes, modo_jogo)


def main():
    parser = argparse.ArgumentParser(description="Termonal com modo Quarteto")
    parser.add_argument('tamanho', type=int, help="Número de letras da palavra")
    parser.add_argument('tentativas', type=int, help="Número de tentativas possíveis")
    parser.add_argument('--modo', type=int, choices=[1, 2, 4], default=1, 
                       help="Modo de jogo: 1 (uma palavra), 2 (duas palavras), 4 (quatro palavras)")
    
    argumentos = parser.parse_args()
    
    dicionario_palavras, lista_pesos, dicionario_equivalentes = carregar_palavras(argumentos.tamanho)

    if len(dicionario_palavras) == 0:
        print(f"Não há palavras com {argumentos.tamanho} letras no léxico.")
        return

    print(f"\nBem-vindo ao jogo Termonal!")
    print(f"Você tem {argumentos.tentativas} tentativas para acertar {argumentos.modo} palavra(s) de {argumentos.tamanho} letras.")
    
    executar_jogo(dicionario_palavras, lista_pesos, argumentos.tentativas, dicionario_equivalentes, argumentos.modo)


if __name__ == "__main__":
    main()