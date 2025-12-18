# Termonal

Um jogo de adivinhação de palavras baseado em linha de comando (CLI) em português.

## Descrição

Termonal é um jogo baseado em terminal inspirado em jogos populares de palavras, adaptado para a língua portuguesa. Ele é executado completamente na sua interface de linha de comando.

O lexer utilizado neste repositório é baseado fortemente no [pt-br](https://github.com/fserb/pt-br), um projeto dedicado ao processamento de textos em português.

## Instalação

### Pelo AUR
```bash
yay -S termonal
```

### Pelo Git
```
git clone https://github.com/viniciuskant/termonal.git --depth 1
cd termonal
python termonal.py 5 6
```


ou para o multiplas palavras ao mesmo tempo:

```
python termonal.py 6 7 --modo 2
python termonal.py 5 8 --modo 4

```
