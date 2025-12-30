#include "termonal.hpp"
#include <ncurses.h>
#include <panel.h>
#include <menu.h>
#include <form.h>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <cstring>

Termo::Termo(int tamanho, int tentativas, int modo) {
    config.tamanho_palavra = tamanho;
    config.max_tentativas = tentativas;
    config.modo_jogo = modo;
    
    tentativas_realizadas = 0;
    palavras_restantes = modo;
    
    win_principal = nullptr;
    win_tentativas = nullptr;
    win_letras = nullptr;
    win_input = nullptr;
    win_status = nullptr;
}

Termo::~Termo() {
    finalizar();
}

void Termo::inicializar_ncurses() {
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
    
    if (has_colors()) {
        start_color();
        inicializar_cores();
    }
    
    refresh();
}

void Termo::inicializar_cores() {
    init_pair(1, COLOR_BLACK, COLOR_WHITE);
    init_pair(2, COLOR_BLACK, COLOR_GREEN);
    init_pair(3, COLOR_BLACK, COLOR_YELLOW);
    init_pair(4, COLOR_BLACK, COLOR_CYAN);
    init_pair(5, COLOR_WHITE, COLOR_BLACK);
    
    init_pair(6, COLOR_YELLOW, COLOR_BLACK);
    init_pair(7, COLOR_CYAN, COLOR_BLACK);
    init_pair(8, COLOR_RED, COLOR_BLACK);
    init_pair(9, COLOR_BLUE, COLOR_BLACK);
    
    init_color(COLOR_CINZA, 500, 500, 500);
    init_color(COLOR_AMARELO, 1000, 700, 0);
    init_color(COLOR_ROSA, 1000, 500, 500);
    
    init_pair(10, COLOR_BLACK, COLOR_CINZA);
    init_pair(11, COLOR_BLACK, COLOR_ROSA);
}

void Termo::criar_janelas() {
    int altura, largura;
    getmaxyx(stdscr, altura, largura);
    
    win_principal = newwin(altura, largura, 0, 0);
    box(win_principal, 0, 0);
    mvwprintw(win_principal, 0, 2, " TERMONAL ");
    wrefresh(win_principal);
    
    int altura_tentativas = altura * 2 / 3 - 4;
    win_tentativas = newwin(altura_tentativas, largura - 4, 2, 2);
    
    int altura_letras = altura / 6;
    win_letras = newwin(altura_letras, largura - 4, altura_tentativas + 3, 2);
    
    win_status = newwin(2, largura - 4, altura - 3, 2);
    
    win_input = newwin(3, largura - 4, altura_tentativas + altura_letras + 4, 2);
    box(win_input, 0, 0);
    mvwprintw(win_input, 0, 2, " Entrada ");
    
    refresh();
}

std::string Termo::normalizar_palavra(const std::string& palavra) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>> conv;
    std::wstring wpalavra = conv.from_bytes(palavra);
    
    std::wstring resultado;
    
    for (wchar_t c : wpalavra) {
        wchar_t normalizado = std::towlower(c);
        
        switch (normalizado) {
            case L'á': case L'à': case L'â': case L'ã': case L'ä': normalizado = L'a'; break;
            case L'é': case L'è': case L'ê': case L'ë': normalizado = L'e'; break;
            case L'í': case L'ì': case L'î': case L'ï': normalizado = L'i'; break;
            case L'ó': case L'ò': case L'ô': case L'õ': case L'ö': normalizado = L'o'; break;
            case L'ú': case L'ù': case L'û': case L'ü': normalizado = L'u'; break;
            case L'ç': normalizado = L'c'; break;
        }
        
        resultado += normalizado;
    }
    
    return conv.to_bytes(resultado);
}

bool Termo::carregar_dicionario(const std::string& caminho) {
    std::ifstream arquivo(caminho);
    if (!arquivo.is_open()) {
        return false;
    }
    
    std::string linha;
    while (std::getline(arquivo, linha)) {
        size_t virgula = linha.find(',');
        if (virgula == std::string::npos) continue;
        
        std::string palavra = linha.substr(0, virgula);
        double peso;
        try {
            peso = std::stod(linha.substr(virgula + 1));
        } catch (...) {
            continue;
        }
        
        if (palavra.length() != config.tamanho_palavra) {
            continue;
        }
        
        std::string normalizada = normalizar_palavra(palavra);
        
        lista_pesos.push_back({palavra, peso});
        
        if (dicionario_equivalentes.find(normalizada) == dicionario_equivalentes.end()) {
            dicionario_equivalentes[normalizada] = {palavra, {palavra}};
        } else {
            dicionario_equivalentes[normalizada].variantes.push_back(palavra);
        }
    }
    
    return !lista_pesos.empty();
}

bool Termo::inicializar() {
    inicializar_ncurses();
    criar_janelas();
    
    if (!carregar_dicionario("../pt-br/icf")) {
        exibir_mensagem("Erro ao carregar dicionário", true);
        return false;
    }
    
    estados_letras.resize(config.modo_jogo);
    for (int i = 0; i < config.modo_jogo; i++) {
        for (char c = 'a'; c <= 'z'; c++) {
            estados_letras[i][c] = BRANCO;
        }
    }
    
    historico_tentativas.resize(config.modo_jogo);
    
    palavras_acertadas.resize(config.modo_jogo, false);
    
    if (config.modo_jogo == 1) {
        palavras_secretas.push_back(selecionar_palavra_secreta());
    } else {
        palavras_secretas = selecionar_palavras_unicas(config.modo_jogo);
    }
    
    cores_palavras = {6, 7, 8, 9};
    
    return true;
}

std::string Termo::selecionar_palavra_secreta() {
    if (lista_pesos.empty()) return "";
    
    std::vector<double> pesos;
    std::vector<std::string> palavras;
    double soma_exp = 0.0;
    
    for (const auto& entrada : lista_pesos) {
        double exp_peso = std::exp(-1.0 * entrada.peso);
        pesos.push_back(exp_peso);
        soma_exp += exp_peso;
        palavras.push_back(entrada.palavra);
    }
    
    std::vector<double> probabilidades;
    for (double peso : pesos) {
        probabilidades.push_back(peso / soma_exp);
    }
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::discrete_distribution<> dist(probabilidades.begin(), probabilidades.end());
    
    return palavras[dist(gen)];
}

std::vector<std::string> Termo::selecionar_palavras_unicas(int quantidade) {
    std::vector<std::string> selecionadas;
    std::set<std::string> usadas;
    
    while (selecionadas.size() < quantidade && selecionadas.size() < lista_pesos.size()) {
        std::string palavra = selecionar_palavra_secreta();
        if (usadas.find(palavra) == usadas.end()) {
            selecionadas.push_back(palavra);
            usadas.insert(palavra);
        }
    }
    
    return selecionadas;
}


void Termo::calcular_feedback(const std::string& secreta, const std::string& tentativa,
                             std::vector<EstadoLetra>& feedback_detalhado) {
    std::string secreta_norm = normalizar_palavra(secreta);
    std::string tentativa_norm = normalizar_palavra(tentativa);
    
    feedback_detalhado.resize(config.tamanho_palavra, CINZA);
    std::vector<bool> usada_secreta(config.tamanho_palavra, false);
    std::vector<bool> usada_tentativa(config.tamanho_palavra, false);
    
    for (int i = 0; i < config.tamanho_palavra; i++) {
        if (tentativa_norm[i] == secreta_norm[i]) {
            feedback_detalhado[i] = VERDE;
            usada_secreta[i] = true;
            usada_tentativa[i] = true;
        }
    }
    
    for (int i = 0; i < config.tamanho_palavra; i++) {
        if (feedback_detalhado[i] == VERDE) continue;
        
        for (int j = 0; j < config.tamanho_palavra; j++) {
            if (!usada_secreta[j] && tentativa_norm[i] == secreta_norm[j]) {
                feedback_detalhado[i] = AMARELO;
                usada_secreta[j] = true;
                break;
            }
        }
    }
    
    for (int i = 0; i < config.tamanho_palavra; i++) {
        if (feedback_detalhado[i] == VERDE || feedback_detalhado[i] == AMARELO) continue;
        feedback_detalhado[i] = BRANCO;
    }
}


void Termo::atualizar_estado_letras(int idx_palavra, const std::vector<EstadoLetra>& feedback,
                                   const std::string& tentativa) {
    std::string tentativa_norm = normalizar_palavra(tentativa);
    
    for (size_t i = 0; i < tentativa_norm.length(); i++) {
        char letra = tentativa_norm[i];
        EstadoLetra estado_atual = estados_letras[idx_palavra][letra];
        EstadoLetra novo_estado = feedback[i];
        
        if (estado_atual == VERDE) continue;
        if (estado_atual == AMARELO && novo_estado != VERDE) continue;
        
        estados_letras[idx_palavra][letra] = novo_estado;
    }
}

void Termo::exibir_quadro_tentativas() {
    limpar_janela(win_tentativas);
    
    int max_historico = 0;
    for (const auto& historico : historico_tentativas) {
        if (historico.size() > max_historico) {
            max_historico = historico.size();
        }
    }
    
    int y = 0;
    int x_inicial = 15;
    
    if (config.modo_jogo == 1) {
        for (size_t tentativa_idx = 0; tentativa_idx < historico_tentativas[0].size(); tentativa_idx++) {
            mvwprintw(win_tentativas, y, 2, "Tentativa %d: ", tentativa_idx + 1);
            
            const auto& tentativa_info = historico_tentativas[0][tentativa_idx];
            const std::string& palavra_tentada = tentativa_info.first;
            const std::vector<EstadoLetra>& feedback = tentativa_info.second;
            
            int x = x_inicial;
            
            for (size_t letra_idx = 0; letra_idx < palavra_tentada.length(); letra_idx++) {
                char letra = std::toupper(palavra_tentada[letra_idx]);
                EstadoLetra estado = feedback[letra_idx];
                
                int cor_par = 5;
                
                switch (estado) {
                    case VERDE:
                        cor_par = 2;
                        break;
                    case AMARELO:
                        cor_par = 3;
                        break;
                    case BRANCO:
                    case CINZA:
                        cor_par = 1;
                        break;
                }
                
                wattron(win_tentativas, COLOR_PAIR(cor_par));
                
                if (estado == BRANCO || estado == CINZA) {
                    wattron(win_tentativas, A_BOLD);
                    mvwprintw(win_tentativas, y, x, "%c", letra);
                    wattroff(win_tentativas, A_BOLD);
                } else {
                    mvwprintw(win_tentativas, y, x, "%c", letra);
                }
                
                wattroff(win_tentativas, COLOR_PAIR(cor_par));
                
                x += 2;
            }
            
            y++;
        }
    } else {
        for (int tentativa_idx = 0; tentativa_idx < max_historico; tentativa_idx++) {
            mvwprintw(win_tentativas, y, 2, "Tentativa %d: ", tentativa_idx + 1);
            
            int x = x_inicial;
            
            for (int palavra_idx = 0; palavra_idx < config.modo_jogo; palavra_idx++) {
                if (tentativa_idx < historico_tentativas[palavra_idx].size()) {
                    const auto& tentativa_info = historico_tentativas[palavra_idx][tentativa_idx];
                    const std::string& palavra_tentada = tentativa_info.first;
                    const std::vector<EstadoLetra>& feedback = tentativa_info.second;
                    
                    for (size_t letra_idx = 0; letra_idx < palavra_tentada.length(); letra_idx++) {
                        char letra = std::toupper(palavra_tentada[letra_idx]);
                        EstadoLetra estado = feedback[letra_idx];
                        
                        int cor_par = 5;
                        
                        switch (estado) {
                            case VERDE:
                                cor_par = 2;
                                break;
                            case AMARELO:
                                cor_par = 3;
                                break;
                            case BRANCO:
                            case CINZA:
                                cor_par = 1;
                                break;
                        }
                        
                        wattron(win_tentativas, COLOR_PAIR(cor_par));
                        
                        if (estado == BRANCO || estado == CINZA) {
                            wattron(win_tentativas, A_BOLD);
                            mvwprintw(win_tentativas, y, x, "%c", letra);
                            wattroff(win_tentativas, A_BOLD);
                        } else {
                            mvwprintw(win_tentativas, y, x, "%c", letra);
                        }
                        
                        wattroff(win_tentativas, COLOR_PAIR(cor_par));
                        
                        x++;
                    }
                } else {
                    x += config.tamanho_palavra;
                }
                
                x += 2;
            }
            
            y++;
        }
    }
    
    wrefresh(win_tentativas);
}


void Termo::exibir_estado_letras() {
    limpar_janela(win_letras);
    
    int y = 0;
    
    if (config.modo_jogo == 1) {
        std::string linha = "Letras: ";
        for (char c = 'a'; c <= 'z'; c++) {
            int cor = 5;
            
            switch (estados_letras[0][c]) {
                case VERDE: cor = 2; break;
                case AMARELO: cor = 3; break;
                case CINZA: cor = 10; break;
                case BRANCO: cor = 5; break;
            }
            
            wattron(win_letras, COLOR_PAIR(cor));
            wprintw(win_letras, "%c ", std::toupper(c));
            wattroff(win_letras, COLOR_PAIR(cor));
        }
    } else {
        for (int i = 0; i < config.modo_jogo; i++) {
            wattron(win_letras, COLOR_PAIR(cores_palavras[i]));
            wprintw(win_letras, "Palavra %d: ", i + 1);
            wattroff(win_letras, COLOR_PAIR(cores_palavras[i]));
            
            for (char c = 'a'; c <= 'z'; c++) {
                int cor = 5; 
                
                switch (estados_letras[i][c]) {
                    case VERDE: cor = 2; break;
                    case AMARELO: cor = 3; break;
                    case CINZA: cor = 10; break;
                    case BRANCO: cor = 5; break;
                }
                
                wattron(win_letras, COLOR_PAIR(cor));
                wprintw(win_letras, "%c ", std::toupper(c));
                wattroff(win_letras, COLOR_PAIR(cor));
            }
            
            y++;
            if (i < config.modo_jogo - 1) {
                wmove(win_letras, y, 0);
            }
        }
    }
    
    wrefresh(win_letras);
}

void Termo::exibir_status() {
    limpar_janela(win_status);
    
    std::string status = "Palavras restantes: " + std::to_string(palavras_restantes) +
                        " | Tentativa: " + std::to_string(tentativas_realizadas + 1) +
                        "/" + std::to_string(config.max_tentativas);
    
    mvwprintw(win_status, 0, 0, "%s", status.c_str());
    
    wattron(win_status, COLOR_PAIR(2));
    wprintw(win_status, " VERDE ");
    wattroff(win_status, COLOR_PAIR(2));
    
    wprintw(win_status, "=Posicao correta | ");
    
    wattron(win_status, COLOR_PAIR(3));
    wprintw(win_status, " AMARELO ");
    wattroff(win_status, COLOR_PAIR(3));
    
    wprintw(win_status, "=Letra existe | ");
    
    wattron(win_status, COLOR_PAIR(1));
    wprintw(win_status, " BRANCO ");
    wattroff(win_status, COLOR_PAIR(1));
    
    wprintw(win_status, "=Letra nao existe");
    
    wrefresh(win_status);
}

void Termo::exibir_mensagem(const std::string& msg, bool erro) {
    limpar_janela(win_input);
    box(win_input, 0, 0);
    
    if (erro) {
        wattron(win_input, COLOR_PAIR(8));
    } else {
        wattron(win_input, COLOR_PAIR(4));
    }
    
    mvwprintw(win_input, 1, 2, "%s", msg.c_str());
    
    if (erro) {
        wattroff(win_input, COLOR_PAIR(8));
    } else {
        wattroff(win_input, COLOR_PAIR(4));
    }
    
    wrefresh(win_input);
}

void Termo::limpar_janela(WINDOW* win) {
    werase(win);
    box(win, 0, 0);
}

std::string Termo::obter_entrada_com_cursor() {
    int pos_cursor = 0;
    int max_letras = config.tamanho_palavra;
    std::string entrada(max_letras, ' '); 
    
    int linha = 1;
    int coluna_inicio = 2 + strlen("Digite uma palavra: ");
    
    keypad(win_input, TRUE);
    noecho();
    curs_set(1);
    
    wmove(win_input, linha, 2);
    wclrtoeol(win_input);
    mvwprintw(win_input, linha, 2, "Digite uma palavra: ");
    
    for (int i = 0; i < max_letras; i++) {
        mvwprintw(win_input, linha, coluna_inicio + i, "_");
    }
    
    wmove(win_input, linha, coluna_inicio + pos_cursor);
    wrefresh(win_input);
    
    int ch;
    bool entrada_completa = false;
    
    while (!entrada_completa) {
        ch = wgetch(win_input);
        
        switch (ch) {
            case KEY_ENTER:
            case '\n':
            case '\r':
                entrada_completa = true;
                break;
                
            case KEY_BACKSPACE:
            case 127:
            case 8:
                if (pos_cursor > 0) {
                    pos_cursor--;
                    entrada[pos_cursor] = ' ';
                    
                    for (int i = 0; i < max_letras; i++) {
                        if (entrada[i] == ' ') {
                            mvwprintw(win_input, linha, coluna_inicio + i, "_");
                        } else {
                            mvwprintw(win_input, linha, coluna_inicio + i, "%c", entrada[i]);
                        }
                    }
                    wmove(win_input, linha, coluna_inicio + pos_cursor);
                    wrefresh(win_input);
                }
                break;
                
            case KEY_LEFT:
                if (pos_cursor > 0) {
                    pos_cursor--;
                    wmove(win_input, linha, coluna_inicio + pos_cursor);
                    wrefresh(win_input);
                }
                break;
                
            case KEY_RIGHT:
                if (pos_cursor < max_letras) {
                    pos_cursor++;
                    wmove(win_input, linha, coluna_inicio + pos_cursor);
                    wrefresh(win_input);
                }
                break;
                
            case KEY_HOME:
                pos_cursor = 0;
                wmove(win_input, linha, coluna_inicio + pos_cursor);
                wrefresh(win_input);
                break;
                
            case KEY_END:
                pos_cursor = max_letras;
                wmove(win_input, linha, coluna_inicio + pos_cursor);
                wrefresh(win_input);
                break;
                
            case KEY_DC: 
                if (pos_cursor < max_letras) {
                    entrada[pos_cursor] = ' ';
                    
                    for (int i = 0; i < max_letras; i++) {
                        if (entrada[i] == ' ') {
                            mvwprintw(win_input, linha, coluna_inicio + i, "_");
                        } else {
                            mvwprintw(win_input, linha, coluna_inicio + i, "%c", entrada[i]);
                        }
                    }
                    wmove(win_input, linha, coluna_inicio + pos_cursor);
                    wrefresh(win_input);
                }
                break;
                
            default:
                if ((std::isalpha(ch) || ch == ' ') && pos_cursor < max_letras) {
                    char letra = std::tolower(ch);
                    
                    entrada[pos_cursor] = letra;
                    
                    if (pos_cursor < max_letras) {
                        pos_cursor++;
                    }
                    
                    for (int i = 0; i < max_letras; i++) {
                        if (entrada[i] == ' ') {
                            mvwprintw(win_input, linha, coluna_inicio + i, "_");
                        } else {
                            mvwprintw(win_input, linha, coluna_inicio + i, "%c", entrada[i]);
                        }
                    }
                    wmove(win_input, linha, coluna_inicio + pos_cursor);
                    wrefresh(win_input);
                } else if (ch == 27) {
                    nodelay(win_input, TRUE);
                    int next_ch = wgetch(win_input);
                    nodelay(win_input, FALSE);
                    
                    if (next_ch == ERR) {
                        entrada = std::string(max_letras, ' ');
                        pos_cursor = 0;
                        
                        for (int i = 0; i < max_letras; i++) {
                            mvwprintw(win_input, linha, coluna_inicio + i, "_");
                        }
                        wmove(win_input, linha, coluna_inicio + pos_cursor);
                        wrefresh(win_input);
                    }
                }
                break;
        }
    }
    
    curs_set(0);
    keypad(win_input, FALSE);
    
    return entrada;
}

void Termo::executar() {
    std::string entrada;
    bool jogo_ativo = true;
    
    while (jogo_ativo && tentativas_realizadas < config.max_tentativas && palavras_restantes > 0) {
        exibir_quadro_tentativas();
        exibir_estado_letras();
        exibir_status();
        
        limpar_janela(win_input);
        box(win_input, 0, 0);
        mvwprintw(win_input, 0, 2, " Entrada ");
        mvwprintw(win_input, 1, 2, "Digite uma palavra (%d letras): ", config.tamanho_palavra);
        wrefresh(win_input);
        
        entrada = obter_entrada_com_cursor();
        
        if (entrada.length() != config.tamanho_palavra) {
            exibir_mensagem("A palavra deve ter " + std::to_string(config.tamanho_palavra) + " letras!", true);
            continue;
        }
        
        std::string entrada_norm = normalizar_palavra(entrada);
        if (dicionario_equivalentes.find(entrada_norm) == dicionario_equivalentes.end()) {
            exibir_mensagem("Palavra não reconhecida!", true);
            continue;
        }
        
        tentativas_realizadas++;
        bool acertou_alguma = false;
        
        for (int i = 0; i < config.modo_jogo; i++) {
            if (palavras_acertadas[i]) continue;
            
            std::string feedback_str;
            std::vector<EstadoLetra> feedback_detalhado;
            
            calcular_feedback(palavras_secretas[i], entrada, feedback_detalhado);
            historico_tentativas[i].push_back({entrada, feedback_detalhado});            
            atualizar_estado_letras(i, feedback_detalhado, entrada);
            
            std::string secreta_norm = normalizar_palavra(palavras_secretas[i]);
            if (entrada_norm == secreta_norm) {
                palavras_acertadas[i] = true;
                palavras_restantes--;
                acertou_alguma = true;
            }
        }
        
        if (acertou_alguma && palavras_restantes == 0) {
            exibir_mensagem("Parabéns! Você acertou todas as palavras!", false);
            jogo_ativo = false;
        }
    }
    
    if (palavras_restantes > 0) {
        exibir_mensagem("Fim de jogo! As palavras eram:", true);
        
        for (int i = 0; i < config.modo_jogo; i++) {
            std::string msg = "Palavra " + std::to_string(i + 1) + ": " + palavras_secretas[i];
            mvwprintw(win_input, 1, 2, "%s", msg.c_str());
            wrefresh(win_input);
            getch();
        }
    }
}

void Termo::finalizar() {
    if (win_input) delwin(win_input);
    if (win_status) delwin(win_status);
    if (win_letras) delwin(win_letras);
    if (win_tentativas) delwin(win_tentativas);
    if (win_principal) delwin(win_principal);
    
    endwin();
}
