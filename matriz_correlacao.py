"""
Calcula a matriz de correlação dos retornos diários de PETR4, VALE3, ITUB4
e IBOV, salva em CSV e plota como heatmap.
"""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

ARQUIVO_ENTRADA = "retornos_2anos.csv"
ARQUIVO_SAIDA = "correlacao_retornos.csv"
ARQUIVO_GRAFICO = "correlacao_heatmap.png"

NOMES = {
    "PETR4.SA": "PETR4",
    "VALE3.SA": "VALE3",
    "ITUB4.SA": "ITUB4",
    "^BVSP": "IBOV",
}
ORDEM = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"]

# Par divergente do skill dataviz: blue <-> red, com neutro cinza no meio
COR_NEGATIVO = "#e34948"   # slot 8 - red
COR_NEUTRO = "#f0efec"     # cinza neutro (superfície clara)
COR_POSITIVO = "#2a78d6"   # slot 1 - blue
CMAP_DIVERGENTE = LinearSegmentedColormap.from_list(
    "diverging_blue_red", [COR_NEGATIVO, COR_NEUTRO, COR_POSITIVO]
)

COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_SURFACE = "#fcfcfb"
COR_GRID = "#e1e0d9"


def main():
    df = pd.read_csv(ARQUIVO_ENTRADA, parse_dates=["Date"])

    retornos_wide = df.pivot(index="Date", columns="Ticker", values="RetornoDiario")
    retornos_wide = retornos_wide[ORDEM].dropna()

    correlacao = retornos_wide.corr()
    correlacao.index = [NOMES[t] for t in correlacao.index]
    correlacao.columns = [NOMES[t] for t in correlacao.columns]
    correlacao.to_csv(ARQUIVO_SAIDA, encoding="utf-8")
    print(f"Matriz de correlação salva em: {ARQUIVO_SAIDA}\n")
    print(correlacao.round(3).to_string())

    n = len(correlacao)
    fig, ax = plt.subplots(figsize=(6.5, 5.5), facecolor=COR_SURFACE)
    ax.set_facecolor(COR_SURFACE)

    im = ax.imshow(correlacao.values, cmap=CMAP_DIVERGENTE, vmin=-1, vmax=1)

    # Espaçador de 2px (superfície) entre células
    ax.set_xticks(np.arange(n + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=COR_SURFACE, linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(correlacao.columns, color=COR_TEXTO_SECUNDARIO, fontsize=10)
    ax.set_yticklabels(correlacao.index, color=COR_TEXTO_SECUNDARIO, fontsize=10)
    ax.tick_params(bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Rótulo direto em cada célula, com cor de texto que garante contraste
    for i in range(n):
        for j in range(n):
            valor = correlacao.values[i, j]
            cor_texto = "#ffffff" if abs(valor) > 0.55 else COR_TEXTO_PRIMARIO
            ax.text(
                j, i, f"{valor:.2f}",
                ha="center", va="center",
                color=cor_texto, fontsize=11, fontweight="bold",
            )

    ax.set_title(
        "Correlação dos retornos diários (2 anos)",
        fontsize=13, color=COR_TEXTO_PRIMARIO, loc="left", fontweight="bold", pad=14,
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlação", color=COR_TEXTO_SECUNDARIO, fontsize=9)
    cbar.ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=8)
    cbar.outline.set_visible(False)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=150, facecolor=COR_SURFACE)
    print(f"\nHeatmap salvo em: {ARQUIVO_GRAFICO}")


if __name__ == "__main__":
    main()
