import sys  # Importa o módulo sys para acessar os argumentos da linha de comando
import json # Importa o módulo json para manipular arquivos JSON
 
# Função para reconhecer uma palavra em um AFD
def recognize_word(afd, word): # Recebe um AFD e uma palavra
    current_state = afd["q0"] # Inicializa o estado atual com o estado inicial
    path = [current_state] # Inicializa o caminho com o estado inicial
 
    for symbol in word: # Itera sobre cada símbolo da palavra
        if symbol not in afd["V"]: # Verifica se o símbolo pertence ao alfabeto
            return f"'{word}' não é reconhecida\n[símbolo '{symbol}' não pertence ao alfabeto]" # Se não pertencer, retorna falso e a mensagem
        try: # Tenta acessar a transição do estado atual com o símbolo atual
            current_state = afd["delta"][current_state][symbol] # Atualiza o estado atual
            path.append(current_state)  
        except KeyError: 
            return "Transição não definida" 
 
    caminho = " -> ".join(path)
    if current_state in afd["F"]: # Verifica se o estado atual é final
        return f"'{word}' é reconhecida\n[caminho: {caminho}]" # Se for final, retorna verdadeiro e o caminho
    else: # Se não for final, retorna falso e o caminho
        return f"'{word}' não é reconhecida\n[caminho {caminho} não é final]"
 
 
# Função para imprimir o conteúdo do arquivo .gv
def print_gv_content(gv_file):
    with open(gv_file, 'r') as file: # Abre o arquivo .gv em modo de leitura
        print(file.read()) # Imprime o conteúdo do arquivo

# Função para salvar um afd em um arquivo JSON
def guarda_gv(afd, arquivo_saida): # Salva o AFD no arquivo de saída
    with open(arquivo_saida, 'w') as file: # Abre o arquivo de saída em modo de escrita
        file.write(afd)

# Função para analisar os argumentos da linha de comando
def parse_arguments(args): 
    json_file = None
    word = None
    graphviz = False
    for i, arg in enumerate(args): # Itera sobre os argumentos
        if arg.endswith('.json'): # Verifica se o argumento é um arquivo JSON
            json_file = arg # Atribui o arquivo JSON à variável json_file
        elif arg == '-rec' and i + 1 < len(args): # Verifica se o argumento é '-rec' e se há um próximo argumento
            word = args[i + 1] # Atribui a palavra ao argumento seguinte
        elif arg == '-graphviz': # Verifica se o argumento é '-graphviz'
            graphviz = True 
    return json_file, word, graphviz # Retorna o arquivo JSON, a palavra e a flag graphviz

# Função para gerar o código Graphviz de um AFD
def generate_graphviz(afd):
    lines = ['digraph afd {'] # Inicializa a lista de linhas com o cabeçalho do arquivo .gv
    lines.append('    node [shape = doublecircle]; ' + ' '.join(afd['F']) + ';')
    lines.append('    node [shape = point]; qi;')
    lines.append('    node [shape = circle];')
 
    # Estado inicial apontando para o primeiro estado
    lines.append('    qi -> ' + afd['q0'] + ';')
 
    # Adiciona as transições
    for start_state, transitions in afd['delta'].items(): # Para cada estado de início
        for input_val, end_state in transitions.items():    # Pode haver mais de uma transição para um mesmo símbolo
            lines.append(f'    {start_state} -> {end_state} [label="{input_val}"];') # Adiciona a transição ao arquivo .gv
 
    lines.append('}') # Fecha o grafo
    dot_representation = '\n'.join(lines) # Junta todas as linhas em uma única string
    print(dot_representation) # Imprime o código Graphviz
    guarda_gv(dot_representation, arquivo_afnd) # Salva o AFD no arquivo de saída

# Verifica se o arquivo JSON foi especificado
if len(sys.argv) < 2:  # Verifica se o número de argumentos é pelo menos o mínimo esperado
    print("!Guia!: python afd-main.py <nome_ficheiro>.json [-rec 'palavra' OU -graphviz <nome_ficheiro>.gv]")
    sys.exit(1)
 
json_file, word, graphviz = parse_arguments(sys.argv[1:]) # Analisa os argumentos da linha de comando
 
# Verifica se o arquivo JSON foi encontrado
if not json_file: 
    print("Arquivo JSON não especificado ou não encontrado.")
    sys.exit(1)
 
# Carrega o AFD do arquivo JSON
with open(json_file, 'r') as file:
    afd = json.load(file)   # Carrega o AFD do arquivo JSON
 
if graphviz:
    if '-graphviz' in sys.argv:
        indice_graphviz = sys.argv.index('-graphviz') # Obtém o índice do argumento output
        if indice_graphviz + 1 < len(sys.argv): # Verifica se há um argumento após o output
            arquivo_afnd = sys.argv[indice_graphviz + 1] # Obtém o nome do arquivo de saída
            generate_graphviz(afd)
elif word:
    print(recognize_word(afd, word))
else:
    # Se nenhum argumento '-rec' foi fornecido, imprime o conteúdo do .gv
    gv_file_path = json_file.rsplit('.', 1)[0] + '.gv'
    print_gv_content(gv_file_path)