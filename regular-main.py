import sys  # Importa o módulo sys para acessar os argumentos da linha de comando
import json # Importa o módulo json para manipular arquivos JSON

# Cria um novo estado e o adiciona à lista de estados
def novoEstado(estados):
    estado = f'q{len(estados)}'
    estados.append(estado)
    return estado

# Função para processar um símbolo
def prc_simbolo(simbolo, simbolos, estados, transicoes):
    inicio = novoEstado(estados) # Cria um novo estado inicial
    fim = novoEstado(estados) # Cria um novo estado final
    transicoes[inicio] = {simbolo: [fim]} # Adiciona a transição do estado inicial para o estado final
    if simbolo not in simbolos: # Adiciona o símbolo à lista de símbolos, se ainda não estiver presente
        simbolos.append(simbolo) # Adiciona o símbolo à lista de símbolos
    return inicio, fim # Retorna o estado inicial e o estado final

# Função para processar um ep
def prc_epsilon(estados, transicoes):
    inicio = novoEstado(estados) # Cria um novo estado inicial
    fim = novoEstado(estados) # Cria um novo estado final
    transicoes[inicio] = {'': [fim]} # Adiciona a transição do estado inicial para o estado final
    return inicio, fim # Retorna o estado inicial e o estado final

# Função para processar uma alternância
def prc_alt(args, estados, simbolos, transicoes):
    inicio = novoEstado(estados) # Cria um novo estado inicial
    fim = novoEstado(estados) # Cria um novo estado final
    for arg in args: # Processa cada argumento da alternância
        subInicio, subFim = converterER(arg, estados, simbolos, transicoes) # Converte o argumento em um AFND
        transicoes.setdefault(inicio, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado inicial para o estado inicial do argumento
        transicoes.setdefault(subFim, {}).setdefault('', []).append(fim) # Adiciona a transição do estado final do argumento para o estado final
    return inicio, fim # Retorna o estado inicial e o estado final

# Função para processar uma sequência
def prc_seq(args, estados, simbolos, transicoes):
    inicioGlobal = None # 
    fimAnterior = None # 
    for arg in args: # Processa cada argumento da sequência
        subInicio, subFim = converterER(arg, estados, simbolos, transicoes) # Converte o argumento em um AFND
        if fimAnterior: # Se houver um estado final anterior 
            transicoes.setdefault(fimAnterior, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado final anterior para o estado inicial do argumento
        else: # Se não houver um estado final anterior
            inicioGlobal = subInicio # O estado inicial global é o estado inicial do argumento
        fimAnterior = subFim # O estado final anterior é o estado final do argumento
    return inicioGlobal, fimAnterior # Retorna o estado inicial global e o estado final

# Função para processar um Kleene
def prc_kle(args, estados, simbolos, transicoes):
    inicio = novoEstado(estados) # Cria um novo estado inicial
    fim = novoEstado(estados) # Cria um novo estado final
    transicoes.setdefault(inicio, {}).setdefault('', []).append(fim) # Adiciona a transição do estado inicial para o estado final
    for arg in args: # Processa cada argumento do Kleene
        subInicio, subFim = converterER(arg, estados, simbolos, transicoes) # Converte o argumento em um AFND
        transicoes.setdefault(inicio, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado inicial para o estado inicial do argumento
        transicoes.setdefault(subFim, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado final do argumento para o estado inicial do argumento
        transicoes.setdefault(subFim, {}).setdefault('', []).append(fim) # Adiciona a transição do estado final do argumento para o estado final
    return inicio, fim # Retorna o estado inicial e o estado final

# Função para processar uma transição
def prc_trans(args, estados, simbolos, transicoes):
    inicio = novoEstado(estados) # Cria um novo estado inicial
    fim = novoEstado(estados) # Cria um novo estado final
    for arg in args: # Processa cada argumento da transição
        subInicio, subFim = converterER(arg, estados, simbolos, transicoes) # Converte o argumento em um AFND
        transicoes.setdefault(inicio, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado inicial para o estado inicial do argumento
        transicoes.setdefault(subFim, {}).setdefault('', []).append(subInicio) # Adiciona a transição do estado final do argumento para o estado inicial do argumento
        transicoes.setdefault(subFim, {}).setdefault('', []).append(fim) # Adiciona a transição do estado final do argumento para o estado final
    return inicio, fim # Retorna o estado inicial e o estado final

# Função para converter uma expressão regular em um AFND
def converterER(er, estados, simbolos, transicoes):
    if 'simb' in er: # Se a expressão regular for um símbolo
        return prc_simbolo(er['simb'], simbolos, estados, transicoes) # Processa o símbolo
    elif 'epsilon' in er: # Se a expressão regular for um epsilon
        return prc_epsilon(estados, transicoes) # Processa o epsilon
    elif er['op'] == 'alt': # Se a expressão regular for uma alternância
        return prc_alt(er['args'], estados, simbolos, transicoes) # Processa a alternância
    elif er['op'] == 'seq': 
        return prc_seq(er['args'], estados, simbolos, transicoes) # Processa a sequência
    elif er['op'] == 'kle':
        return prc_kle(er['args'], estados, simbolos, transicoes) # Processa o Kleene
    elif er['op'] == 'trans':
        return prc_trans(er['args'], estados, simbolos, transicoes) # Processa a transição
    else:
        raise ValueError(f"Operação inválida: {er['op']}") # Se a operação não for válida, lança um erro

# Função para converter uma expressão regular em um AFND
def ConverterToAFND(expression):
    simbolos = [] # Lista de símbolos
    estados = [] # Lista de estados
    transicoes = {} # Dicionário de transições
    inicio, fim = converterER(expression, estados, simbolos, transicoes) # Converte a expressão regular em um AFND
    if fim not in transicoes: # Se o estado final não tiver transições
        transicoes[fim] = {'': []} # Adiciona uma transição vazia
    afnd = { # Cria o AFND
        "V": simbolos,
        "Q": estados,
        "delta": transicoes,
        "q0": inicio,
        "F": [fim]
    }
    return afnd # Retorna o AFND

# Função para ler um arquivo JSON
def read_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Função para salvar um AFND em um arquivo JSON
def save_afnd_to_json(afnd, output_filepath):
    with open(output_filepath, 'w') as file:
        json.dump(afnd, file, indent=2)

# Verifica se o número de argumentos é pelo menos o mínimo esperado
if len(sys.argv) < 3:
    print("!Guia!: python regular-main.py <nome_ficheiro>.json -output <OUTPUT_FILE.json>")
    sys.exit(1)

# Processa os argumentos da linha de comando
input_filepath = sys.argv[1]
output_filepath = 'afnd.json'  # Um valor padrão, caso '--output' não seja especificado

# Procura pelo argumento '--output' e captura o valor especificado logo após
if "-output" in sys.argv:
    output_index = sys.argv.index("-output") + 1
    if output_index < len(sys.argv):
        output_filepath = sys.argv[output_index]
    else:
        print("Falta escrever o nome do ficheiro!")
        sys.exit(1)

# Carrega a expressão regular do arquivo de entrada e converte para AFND
expression = read_json_file(input_filepath)
afnd = ConverterToAFND(expression)

# Salva o AFND resultante no arquivo de saída especificado
save_afnd_to_json(afnd, output_filepath)
print(f"AFND saved to {output_filepath}")