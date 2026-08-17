"""
Pipeline completo do projeto Rota Inteligente (Sabor Express):

1. Carrega o grafo da cidade (bairros + ruas).
2. Roda A*, BFS e DFS do restaurante ate cada pedido e compara os custos.
3. Agrupa os pedidos em zonas de entrega com K-Means.
4. Gera os graficos usados no README (docs/grafo_cidade.png,
   docs/clusters_entregas.png, docs/comparacao_algoritmos.png)
   e um resumo em texto (docs/resultados.txt).
"""
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from clustering import agrupar, carregar_pedidos, escolher_k
from grafo import a_estrela, bfs, carregar_grafo, custo_do_caminho, dfs

DEPOSITO = 0  # Centro - Sabor Express


def construir_nx(adj):
    G = nx.Graph()
    for o in adj:
        for d, w in adj[o]:
            G.add_edge(o, d, weight=w)
    return G


def desenhar_grafo_cidade(adj, coords, nomes):
    G = construir_nx(adj)
    pos = {i: coords[i] for i in coords}

    plt.figure(figsize=(9, 7))
    cores = ["#d62728" if n == DEPOSITO else "#1f77b4" for n in G.nodes]
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=650)
    nx.draw_networkx_labels(
        G, pos, labels={n: nomes[n] for n in G.nodes}, font_size=8
    )
    pesos = nx.get_edge_attributes(G, "weight")
    pesos_fmt = {k: f"{v:.1f}" for k, v in pesos.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos_fmt, font_size=7)

    plt.title("Grafo da cidade — bairros e tempo estimado (min) entre eles\n(nó vermelho = restaurante Sabor Express)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("docs/grafo_cidade.png", dpi=150)
    plt.close()
    print("[ok] docs/grafo_cidade.png gerado")


def comparar_algoritmos(adj, coords, nomes):
    destinos = [n for n in coords if n != DEPOSITO]
    linhas = []
    for destino in destinos:
        caminho_astar, custo_astar, visit_astar = a_estrela(adj, coords, DEPOSITO, destino)
        caminho_bfs, visit_bfs = bfs(adj, DEPOSITO, destino)
        caminho_dfs, visit_dfs = dfs(adj, DEPOSITO, destino)

        custo_bfs = custo_do_caminho(adj, caminho_bfs)
        custo_dfs = custo_do_caminho(adj, caminho_dfs)

        linhas.append({
            "destino": nomes[destino],
            "custo_astar_min": round(custo_astar, 2),
            "nos_visitados_astar": visit_astar,
            "custo_bfs_min": round(custo_bfs, 2),
            "nos_visitados_bfs": visit_bfs,
            "custo_dfs_min": round(custo_dfs, 2),
            "nos_visitados_dfs": visit_dfs,
        })
    return linhas


def graficos_comparacao(linhas):
    destinos = [l["destino"] for l in linhas]
    astar = [l["custo_astar_min"] for l in linhas]
    bfs_c = [l["custo_bfs_min"] for l in linhas]
    dfs_c = [l["custo_dfs_min"] for l in linhas]

    x = range(len(destinos))
    largura = 0.27
    plt.figure(figsize=(11, 6))
    plt.bar([i - largura for i in x], astar, width=largura, label="A*", color="#2ca02c")
    plt.bar(list(x), bfs_c, width=largura, label="BFS", color="#1f77b4")
    plt.bar([i + largura for i in x], dfs_c, width=largura, label="DFS", color="#d62728")
    plt.xticks(list(x), destinos, rotation=35, ha="right")
    plt.ylabel("Tempo estimado do trajeto (min)")
    plt.title("Custo do trajeto do restaurante até cada bairro: A* vs BFS vs DFS")
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/comparacao_algoritmos.png", dpi=150)
    plt.close()
    print("[ok] docs/comparacao_algoritmos.png gerado")


def desenhar_clusters(ids, pontos, labels, centros, coords, nomes):
    plt.figure(figsize=(9, 7))
    cmap = plt.get_cmap("tab10")
    for zona in sorted(set(labels)):
        pts = pontos[labels == zona]
        plt.scatter(pts[:, 0], pts[:, 1], color=cmap(zona), label=f"Zona {zona}", s=70)
    plt.scatter(centros[:, 0], centros[:, 1], color="black", marker="X", s=180, label="Centróides")
    dx, dy = coords[DEPOSITO]
    plt.scatter([dx], [dy], color="red", marker="*", s=300, label="Sabor Express (depósito)")

    plt.title("Agrupamento dos pedidos em zonas de entrega (K-Means)")
    plt.xlabel("x (km)")
    plt.ylabel("y (km)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/clusters_entregas.png", dpi=150)
    plt.close()
    print("[ok] docs/clusters_entregas.png gerado")


def main():
    adj, coords, nomes = carregar_grafo()
    desenhar_grafo_cidade(adj, coords, nomes)

    linhas = comparar_algoritmos(adj, coords, nomes)
    graficos_comparacao(linhas)

    ids, pontos = carregar_pedidos()
    melhor_k, scores = escolher_k(pontos)
    labels, centros, inertia = agrupar(pontos, melhor_k)
    desenhar_clusters(ids, pontos, labels, centros, coords, nomes)

    # ----- resumo em texto para consulta / conferencia -----
    ganho_medio = sum(l["custo_bfs_min"] - l["custo_astar_min"] for l in linhas) / len(linhas)
    ganho_pct = ganho_medio / (sum(l["custo_bfs_min"] for l in linhas) / len(linhas)) * 100
    media_visitados_astar = sum(l["nos_visitados_astar"] for l in linhas) / len(linhas)
    media_visitados_bfs = sum(l["nos_visitados_bfs"] for l in linhas) / len(linhas)

    resumo = {
        "comparacao_por_destino": linhas,
        "ganho_medio_min_astar_vs_bfs": round(ganho_medio, 2),
        "ganho_medio_percentual_astar_vs_bfs": round(ganho_pct, 1),
        "media_nos_visitados_astar": round(media_visitados_astar, 2),
        "media_nos_visitados_bfs": round(media_visitados_bfs, 2),
        "kmeans_silhouette_por_k": {k: round(v, 3) for k, v in scores.items()},
        "kmeans_k_escolhido": melhor_k,
        "kmeans_inertia": round(inertia, 2),
    }

    with open("docs/resultados.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(resumo, ensure_ascii=False, indent=2))

    print("\n===== RESUMO =====")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
