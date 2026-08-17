"""
Modelagem da cidade como grafo e algoritmos de busca de caminho.

- Bairros/pontos de entrega -> nos do grafo
- Ruas -> arestas com peso (tempo estimado em minutos)
- Algoritmos implementados: A* (com heuristica de distancia euclidiana),
  BFS e DFS (usados como baseline de comparacao, ignorando peso das arestas).
"""
import csv
import heapq
import math
from collections import deque

BAIRROS_CSV = "data/bairros.csv"
RUAS_CSV = "data/ruas.csv"


def carregar_grafo():
    coords = {}
    nomes = {}
    with open(BAIRROS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            i = int(row["id"])
            coords[i] = (float(row["x_km"]), float(row["y_km"]))
            nomes[i] = row["nome"]

    adj = {i: [] for i in coords}
    with open(RUAS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            o, d = int(row["origem"]), int(row["destino"])
            tempo = float(row["tempo_min"])
            adj[o].append((d, tempo))
            adj[d].append((o, tempo))  # ruas de mao dupla

    return adj, coords, nomes


def heuristica(a, b, coords, velocidade_max_kmh=60):
    """Distancia euclidiana convertida em tempo minimo possivel (minutos).
    Admissivel: nenhuma rua real e percorrida mais rapido que a velocidade
    maxima considerada, entao a heuristica nunca superestima o custo real."""
    xa, ya = coords[a]
    xb, yb = coords[b]
    dist_km = math.hypot(xb - xa, yb - ya)
    return dist_km / velocidade_max_kmh * 60  # minutos


def a_estrela(adj, coords, origem, destino):
    """Retorna (caminho, custo_min, nos_visitados)."""
    aberto = [(heuristica(origem, destino, coords), 0.0, origem, [origem])]
    custo_g = {origem: 0.0}
    visitados = set()

    while aberto:
        f, g, atual, caminho = heapq.heappop(aberto)
        if atual == destino:
            return caminho, g, len(visitados)
        if atual in visitados:
            continue
        visitados.add(atual)

        for vizinho, peso in adj[atual]:
            novo_g = g + peso
            if novo_g < custo_g.get(vizinho, math.inf):
                custo_g[vizinho] = novo_g
                h = heuristica(vizinho, destino, coords)
                heapq.heappush(aberto, (novo_g + h, novo_g, vizinho, caminho + [vizinho]))

    return None, math.inf, len(visitados)


def bfs(adj, origem, destino):
    """Busca em largura: acha caminho com MENOS arestas, ignora peso."""
    fila = deque([(origem, [origem])])
    visitados = {origem}
    while fila:
        atual, caminho = fila.popleft()
        if atual == destino:
            return caminho, len(visitados)
        for vizinho, _ in adj[atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))
    return None, len(visitados)


def dfs(adj, origem, destino):
    """Busca em profundidade: acha UM caminho valido, sem garantia de otimalidade."""
    pilha = [(origem, [origem])]
    visitados = set()
    while pilha:
        atual, caminho = pilha.pop()
        if atual == destino:
            return caminho, len(visitados)
        if atual in visitados:
            continue
        visitados.add(atual)
        for vizinho, _ in adj[atual]:
            if vizinho not in visitados:
                pilha.append((vizinho, caminho + [vizinho]))
    return None, len(visitados)


def custo_do_caminho(adj, caminho):
    pesos = {}
    for o in adj:
        for d, w in adj[o]:
            pesos[(o, d)] = w
    return sum(pesos[(caminho[i], caminho[i + 1])] for i in range(len(caminho) - 1))


if __name__ == "__main__":
    adj, coords, nomes = carregar_grafo()
    origem = 0
    for destino in [8, 9, 10]:
        caminho, custo, visitados = a_estrela(adj, coords, origem, destino)
        nomes_caminho = " -> ".join(nomes[n] for n in caminho)
        print(f"A* {nomes[origem]} -> {nomes[destino]}: {custo:.2f} min | {nomes_caminho}")
