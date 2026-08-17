"""
Agrupamento dos pedidos em zonas de entrega usando K-Means.

Em horarios de pico, em vez de mandar um entregador de cada vez para um
pedido isolado (abordagem atual, manual, da Sabor Express), os pedidos sao
agrupados em zonas geograficas. Cada zona e atendida por um unico
entregador, que sai do restaurante, percorre as entregas da sua zona e
retorna -- reduzindo deslocamento total e numero de viagens ociosas.
"""
import csv

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

PEDIDOS_CSV = "data/pedidos.csv"


def carregar_pedidos():
    ids, pontos = [], []
    with open(PEDIDOS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ids.append(int(row["id_pedido"]))
            pontos.append([float(row["x_km"]), float(row["y_km"])])
    return ids, np.array(pontos)


def escolher_k(pontos, k_min=2, k_max=5):
    """Escolhe o numero de zonas (k) pelo melhor silhouette score."""
    melhor_k, melhor_score = k_min, -1
    scores = {}
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(pontos)
        score = silhouette_score(pontos, km.labels_)
        scores[k] = score
        if score > melhor_score:
            melhor_k, melhor_score = k, score
    return melhor_k, scores


def agrupar(pontos, k):
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(pontos)
    return km.labels_, km.cluster_centers_, km.inertia_


if __name__ == "__main__":
    ids, pontos = carregar_pedidos()
    melhor_k, scores = escolher_k(pontos)
    labels, centros, inertia = agrupar(pontos, melhor_k)

    print("Silhouette score por k:", {k: round(v, 3) for k, v in scores.items()})
    print(f"k escolhido: {melhor_k} (maior silhouette score)")
    print(f"Inertia (soma das distancias^2 aos centroides): {inertia:.2f}")
    for zona in range(melhor_k):
        pedidos_zona = [ids[i] for i in range(len(ids)) if labels[i] == zona]
        print(f"Zona {zona} (centro {centros[zona].round(2)}): pedidos {pedidos_zona}")
