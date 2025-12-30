#include "termonal.hpp"
#include <iostream>
#include <cstdlib>

void mostrar_uso() {
    std::cout << "Uso: termo <tamanho> <tentativas> [--modo 1|2|4]\n";
    std::cout << "Exemplo:\n";
    std::cout << "  termo 5 6            # 5 letras, 6 tentativas, modo único\n";
    std::cout << "  termo 5 8 --modo 4   # 5 letras, 8 tentativas, quarteto\n";
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        mostrar_uso();
        return 1;
    }
    
    int tamanho = std::atoi(argv[1]);
    int tentativas = std::atoi(argv[2]);
    int modo = 1;
    
    // Processar argumentos opcionais
    for (int i = 3; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--modo" && i + 1 < argc) {
            modo = std::atoi(argv[++i]);
            if (modo != 1 && modo != 2 && modo != 4) {
                std::cerr << "Modo deve ser 1, 2 ou 4\n";
                return 1;
            }
        }
    }
    
    if (tamanho < 3 || tamanho > 10) {
        std::cerr << "Tamanho da palavra deve estar entre 3 e 10\n";
        return 1;
    }
    
    if (tentativas < 1 || tentativas > 20) {
        std::cerr << "Número de tentativas deve estar entre 1 e 20\n";
        return 1;
    }
    
    try {
        Termo jogo(tamanho, tentativas, modo);
        
        
        if (!jogo.inicializar()) {
            return 1;
        }
        
        jogo.executar();
        
        // Aguardar antes de sair
        std::cout << "\nPressione Enter para sair...";
        std::cin.get();
        
    } catch (const std::exception& e) {
        std::cerr << "Erro: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
