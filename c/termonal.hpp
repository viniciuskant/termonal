#ifndef TERMONAL_HPP
#define TERMONAL_HPP

#include <ncurses.h>
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <set>
#include <random>
#include <memory>
#include <fstream>
#include <algorithm>
#include <cmath>
#include <locale>
#include <codecvt>

#define COLOR_CINZA 8
#define COLOR_AMARELO 9
#define COLOR_ROSA 10

enum EstadoLetra {
    BRANCO,
    CINZA,
    AMARELO,
    VERDE
};

struct ConfigJogo {
    int tamanho_palavra;
    int max_tentativas;
    int modo_jogo;
};

struct EntradaDicionario {
    std::string palavra;
    double peso;
};

struct PalavraInfo {
    std::string palavra;
    std::vector<std::string> variantes;
};

class Termo {
private:
    ConfigJogo config;
    std::map<std::string, PalavraInfo> dicionario_equivalentes;
    std::vector<EntradaDicionario> lista_pesos;
    std::vector<std::string> palavras_secretas;
    
    std::vector<std::map<char, EstadoLetra>> estados_letras;
    std::vector<std::vector<std::pair<std::string, std::vector<EstadoLetra>>>> historico_tentativas;
    std::vector<bool> palavras_acertadas;
    int palavras_restantes;
    int tentativas_realizadas;
    
    std::vector<int> cores_palavras;
    
    WINDOW* win_principal;
    WINDOW* win_tentativas;
    WINDOW* win_letras;
    WINDOW* win_input;
    WINDOW* win_status;
    
    void inicializar_ncurses();
    void inicializar_cores();
    void criar_janelas();
    
    bool carregar_dicionario(const std::string& caminho);
    std::string normalizar_palavra(const std::string& palavra);
    
    std::string selecionar_palavra_secreta();
    std::vector<std::string> selecionar_palavras_unicas(int quantidade);
    void calcular_feedback(const std::string& secreta, const std::string& tentativa,
                           std::vector<EstadoLetra>& feedback_detalhado);
    void atualizar_estado_letras(int idx_palavra, const std::vector<EstadoLetra>& feedback,
                                const std::string& tentativa);
    
    std::string obter_entrada_com_cursor();
    void exibir_quadro_tentativas();
    void exibir_estado_letras();
    void exibir_status();
    void limpar_janela(WINDOW* win);
    void exibir_mensagem(const std::string& msg, bool erro = false);
    
public:
    Termo(int tamanho, int tentativas, int modo);
    ~Termo();
    
    bool inicializar();
    void executar();
    void finalizar();
};

#endif