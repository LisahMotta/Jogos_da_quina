import random

grupos = {
    "A": list(range(1, 11)),
    "B": list(range(11, 21)),
    "C": list(range(21, 31)),
    "D": list(range(31, 41)),
    "E": list(range(41, 51)),
    "F": list(range(51, 61)),
    "G": list(range(61, 71)),
    "H": list(range(71, 81)),
}

padroes = [
    ["A", "C", "E", "G", "H"],
    ["A", "B", "D", "F", "H"],
    ["B", "C", "D", "E", "F"],
    ["A", "D", "E", "G", "H"],
]

def gerar_jogo(padrao):
    jogo = []
    for letra in padrao:
        jogo.append(random.choice(grupos[letra]))
    return sorted(jogo)

def validar_jogo(jogo):
    pares = sum(1 for n in jogo if n % 2 == 0)
    return pares in [2, 3]

def gerar_jogos(qtd):
    jogos = []

    while len(jogos) < qtd:
        padrao = random.choice(padroes)
        jogo = gerar_jogo(padrao)

        if validar_jogo(jogo) and jogo not in jogos:
            jogos.append(jogo)

    return jogos