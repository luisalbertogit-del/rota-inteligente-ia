"""
Gera os arquivos de dados do projeto Sabor Express:
- data/bairros.csv      -> nos do grafo (bairros) com coordenadas (ja existe, mantido)
- data/ruas.csv         -> arestas do grafo (ruas) com distancia e tempo estimado
- data/pedidos.csv      -> pontos de entrega (pedidos) do dia, usados no K-Means

Uso: python src/gerar_dados.py
"""
import csv
import math
import random

random.seed(42)  # reprodutibilidade

BAIRROS_CSV = "data/bairros.csv"
RUAS_CSV = "data/ruas.csv"
PEDIDOS_CSV = "data/pedidos.csv"

# Fator de congestionamento por rua (>= 1.0) simula transito real.
# tempo_min = distancia_km * fator  (fator=1.0 equivale a 60 km/h, o teto de velocidade
# considerado; por isso a heuristica de distancia em linha reta usada no A* nunca
# superestima o custo real -> heuristica admissivel)
RUAS = [
    (0, 1, 1.10),
    (0, 3, 1.30),
    (0, 11, 1.05),
    (1, 2, 1.20),
    (1, 3, 1.15),
    (1, 5, 1.40),
    (2, 4, 1.10),
    (2, 5, 1.25),
    (2, 6, 1.15),
    (3, 4, 1.35),
    (3, 7, 1.10),
    (3, 11, 1.05),
    (4, 7, 1.20),
    (4, 8, 1.15),
    (5, 6, 1.30),
    (5, 9, 1.10),
    (5, 10, 1.05),
    (6, 8, 1.25),
    (6, 9, 1.15),
    (7, 8, 1.30),
    # Avenidas diretas que ligam o Centro a bairros mais distantes: em linha
    # reta parecem a escolha obvia (e sao o que um entregador guiado so pela
    # experiencia tende a escolher), mas sofrem com congestionamento forte
    # no horario de pico -> fator de tempo bem mais alto.
    (0, 8, 2.60),
    (0, 9, 2.20),
]


def carregar_bairros():
    bairros = {}
    with open(BAIRROS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bairros[int(row["id"])] = (float(row["x_km"]), float(row["y_km"]), row["nome"])
    return bairros


def gerar_ruas(bairros):
    with open(RUAS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origem", "destino", "distancia_km", "tempo_min"])
        for o, d, fator in RUAS:
            xo, yo, _ = bairros[o]
            xd, yd, _ = bairros[d]
            dist = math.hypot(xd - xo, yd - yo)
            tempo = round(dist * fator, 2)
            w.writerow([o, d, round(dist, 2), tempo])
    print(f"[ok] {len(RUAS)} ruas gravadas em {RUAS_CSV}")


def gerar_pedidos(bairros, n=18):
    """Gera pedidos (entregas) espalhados perto dos bairros residenciais,
    simulando o horario de pico de almoco/jantar."""
    bairros_residenciais = [i for i in bairros if i != 0]  # 0 = restaurante/deposito
    with open(PEDIDOS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id_pedido", "bairro_ref", "x_km", "y_km"])
        for i in range(1, n + 1):
            bairro = random.choice(bairros_residenciais)
            bx, by, _ = bairros[bairro]
            # dispersa o pedido em torno do centro do bairro (+/- 0.6 km)
            x = round(bx + random.uniform(-0.6, 0.6), 2)
            y = round(by + random.uniform(-0.6, 0.6), 2)
            w.writerow([i, bairro, x, y])
    print(f"[ok] {n} pedidos gravados em {PEDIDOS_CSV}")


if __name__ == "__main__":
    bairros = carregar_bairros()
    gerar_ruas(bairros)
    gerar_pedidos(bairros)
