import sys  # Importa o módulo sys para acessar os argumentos da linha de comando
import json # Importa o módulo json para manipular arquivos JSON

# Função para ler um arquivo JSON
def ler_afnd(arquivo_json):
    with open(arquivo_json, 'r') as file:  # Abre o arquivo .json em modo de leitura
        afnd = json.load(file) # Carrega o conteúdo do arquivo JSON
    return afnd

# Função para converter um afdn em um afd
def converter_para_afd(afnd):
    V = afnd['V']  # Símbolos de entrada
    Q = afnd['Q']  # Estados do AFND
    delta = afnd['delta']  # Função de transição do AFND
    q0 = afnd['q0']  # Estado inicial do AFND
    F = afnd['F']  # Estados finais do AFND

    # Calculando o fechamento épsilon do estado inicial
    def epsilon_closure(state_set): # Função para calcular o fechamento épsilon de um conjunto de estados
        closure = set(state_set) # Inicializa o fechamento épsilon com o conjunto de estados
        stack = list(state_set) # Inicializa a pilha com o conjunto de estados
        while stack: # Enquanto a pilha não estiver vazia
            state = stack.pop() # Remove um estado da pilha
            if state in delta and "" in delta[state]: # Se o estado tiver transição por épsilon
                for next_state in delta[state][""]: # Para cada estado alcançável por épsilon
                    if next_state not in closure: # Se o estado ainda não estiver no fechamento épsilon
                        closure.add(next_state) # Adiciona o estado ao fechamento épsilon
                        stack.append(next_state) # Adiciona o estado à pilha
        return closure

    # Inicialização do AFD
    estado_inicial_afd = frozenset(epsilon_closure([q0])) # Estado inicial do AFD
    queue = [estado_inicial_afd]                          # Fila de estados a serem processados
    estados_afd = {estado_inicial_afd: "q0"}              # Mapeamento de estados do AFD
    transicoes_afd = {}                                    # Função de transição do AFD
    estados_finais_afd = set()                              # Estados finais do AFD
    contador = 1                                     # Contador para nomear novos estados

    # Processamento da fila para construção do AFD
    while queue: # Enquanto a fila não estiver vazia
        estado_atual = queue.pop(0) # Remove o primeiro estado da fila
        current_state_name = estados_afd[estado_atual] # Nome do estado atual

        transicoes_afd[current_state_name] = {} # Inicializa as transições do estado atual

        # Processamento para cada símbolo do alfabeto
        for simbolo in V:  
            # Descobrir o conjunto de estados alcançáveis pelo símbolo
            reach = set() # Conjunto de estados alcançáveis pelo símbolo
            for subestado in estado_atual: # Para cada estado do conjunto atual
                if simbolo in delta.get(subestado, {}): # Se houver transição pelo símbolo
                    reach.update(delta[subestado][simbolo]) # Adiciona os estados alcançáveis ao conjunto
            reach_closure = epsilon_closure(reach) # Calcula o fechamento épsilon do conjunto de estados alcançáveis

            if reach_closure: # Se o conjunto de estados alcançáveis não for vazio
                reach_closure = frozenset(reach_closure) # Transforma o conjunto em um conjunto imutável
                if reach_closure not in estados_afd: # Se o conjunto de estados não estiver mapeado
                    estados_afd[reach_closure] = f"q{contador}" # Mapeia o conjunto de estados
                    contador += 1 # Incrementa o contador
                    queue.append(reach_closure) # Adiciona o conjunto de estados à fila
                
                # Adicionando transição
                transicoes_afd[current_state_name][simbolo] = estados_afd[reach_closure] # Adiciona a transição ao AFD

        # Verificando se é um estado final
        if any(state in F for state in estado_atual): # Se algum estado do conjunto atual for final
            estados_finais_afd.add(current_state_name) # Adiciona o estado atual aos estados finais do AFD

    afd = {
        "V": V,
        "Q": list(estados_afd.values()),
        "delta": transicoes_afd,
        "q0": "q0",
        "F": list(estados_finais_afd)
    }

    return afd
 
# Função para salvar um afd em um arquivo JSON
def guarda_afd(afd, arquivo_saida): # Salva o AFD no arquivo de saída
    with open(arquivo_saida, 'w') as file: # Abre o arquivo de saída em modo de escrita
        json.dump(afd, file, indent=4) 

# Função para salvar um afd em um arquivo JSON
def guarda_gv(afd, arquivo_saida): # Salva o AFD no arquivo de saída
    with open(arquivo_saida, 'w') as file: # Abre o arquivo de saída em modo de escrita
        file.write(afd) 

# Função para gerar o código Graphviz da AFD
def generate_graphviz(afnd):
    linhas = ['digraph afnd {']
    linhas.append('    node [shape = doublecircle]; ' + ' '.join(afnd['F']) + ';') # Adiciona os estados finais 
    linhas.append('    node [shape = point]; qi;') # Adiciona o estado inicial
    linhas.append('    node [shape = circle];') # Adiciona os estados intermediários
 
    # Estado inicial apontando para o primeiro estado
    linhas.append('    qi -> ' + afnd['q0'] + ';') # Adiciona a transição do estado inicial para o primeiro estado 
 
    # Adiciona as transições
    for start_state, transitions in afnd['delta'].items(): # Para cada estado de início
        for input_val, end_states in transitions.items(): # Pode haver mais de uma transição para um mesmo símbolo
            for end_state in end_states: # Pode haver mais de um estado final
                linhas.append(f'    {start_state} -> {end_state} [label="{input_val}"];') # Adiciona a transição
 
    linhas.append('}') # Fecha o grafo
    representacao_dot = '\n'.join(linhas) # Junta todas as linhas em uma única string
    print(representacao_dot)  # Imprime o código Graphviz
    guarda_gv(representacao_dot, arquivo_afnd) # Salva o AFD no arquivo de saída
 
# Carrega o AFND do arquivo JSON
if len(sys.argv) < 2: # Verifica se o número de argumentos é pelo menos o mínimo esperado
    print("!Guia!: python afnd-main.py <nome_ficheiro>.json [-graphviz <novo_nome_ficheiro.gv> OU -output <novo_nome_ficheiro.json>]") 
    sys.exit(1)
 
# Assume que o primeiro argumento é o arquivo JSON
arquivo_afnd = sys.argv[1]
afnd = ler_afnd(arquivo_afnd)
afd = converter_para_afd(afnd)
 
# Verifica se o argumento graphviz foi passado
if '-graphviz' in sys.argv:
    indice_graphviz = sys.argv.index('-graphviz') # Obtém o índice do argumento output
    if indice_graphviz + 1 < len(sys.argv): # Verifica se há um argumento após o output
        arquivo_afnd = sys.argv[indice_graphviz + 1] # Obtém o nome do arquivo de saída
        generate_graphviz(afnd)
 
# Verifica se o argumento output foi passado
elif '-output' in sys.argv:     # Verifica se o argumento output foi passado
    indice_output = sys.argv.index('-output') # Obtém o índice do argumento output
    if indice_output + 1 < len(sys.argv): # Verifica se há um argumento após o output
        arquivo_afnd = sys.argv[indice_output + 1] # Obtém o nome do arquivo de saída
        guarda_afd(afd, arquivo_afnd) # Salva o AFD no arquivo de saída
    else:
        print("Erro: Especifique o arquivo de saída após '-output'.") 
else:
    print("Comando não reconhecido.")