"""
Plota a evolução do drawdown (queda em relação ao pico anterior) ao longo
do tempo para PETR4, VALE3, ITUB4 e IBOV, a partir de retornos_2anos.csv.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd

ARQUIVO_ENTRADA = "retornos_2anos.csv"
ARQUIVO_GRAFICO = "drawdown.png"

# Mesma paleta categórica e ordem usadas no gráfico de retorno acumulado
CORES = {
    "PETR4.SA": "#2a78d6",  # slot 1 - blue
    "VALE3.SA": "#eb6834",  # slot 2 - orange
    "ITUB4.SA": "#1baf7a",  # slot 3 - aqua
    "^BVSP": "#eda100",     # slot 4 - yellow
}
NOMES = {
    "PETR4.SA": "PETR4",
    "VALE3.SA": "VALE3",
    "ITUB4.SA": "ITUB4",
    "^BVSP": "IBOV",
}
ORDEM = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"]

COR_GRID = "#e1e0d9"
COR_EIXO = "#c3c2b7"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_SURFACE = "#fcfcfb"


def calcular_drawdown(precos: pd.Series) -> pd.Series:
    pico = precos.cummax()
    return precos / pico - 1


def main():
    df = pd.read_csv(ARQUIVO_ENTRADA, parse_dates=["Date"])
    df = df.sort_values(["Ticker", "Date"]).copy()
    df["Drawdown"] = df.groupby("Ticker")["Close"].transform(calcular_drawdown)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COR_SURFACE)
    ax.set_facecolor(COR_SURFACE)

    for ticker in ORDEM:
        serie = df[df["Ticker"] == ticker]
        ax.plot(
            serie["Date"],
            serie["Drawdown"] * 100,
            label=NOMES[ticker],
            color=CORES[ticker],
            linewidth=1.6,
            solid_capstyle="round",
        )

    # Marca o ponto de drawdown máximo de cada ativo (sem texto solto no
    # gráfico, para evitar colisão entre rótulos quando os fundos ficam
    # próximos em data/valor — o resumo vai num painel à parte).
    minimos = []
    for ticker in ORDEM:
        serie = df[df["Ticker"] == ticker]
        idx_min = serie["Drawdown"].idxmin()
        ponto = serie.loc[idx_min]
        ax.scatter(
            [ponto["Date"]], [ponto["Drawdown"] * 100],
            color=CORES[ticker], s=32, zorder=5, edgecolor=COR_SURFACE, linewidth=1.2,
        )
        minimos.append((ticker, ponto["Drawdown"] * 100))

    # Painel-resumo com o drawdown máximo de cada ativo, ordenado do pior
    # para o melhor, para não competir por espaço com as linhas do gráfico.
    # Um único bloco de texto (cor por linha) sobre uma caixa; a cor de cada
    # linha já basta para ligar ao ativo, já que os pontos na curva usam a
    # mesma cor e a legenda no rodapé nomeia cada série.
    minimos.sort(key=lambda t: t[1])

    titulo_y = 0.25
    passo = 0.043
    altura_caixa = 0.05 + (len(minimos) + 1) * passo

    ax.add_patch(
        plt.Rectangle(
            (0.01, titulo_y - altura_caixa + 0.045),
            0.185,
            altura_caixa,
            transform=ax.transAxes,
            facecolor=COR_SURFACE,
            edgecolor=COR_GRID,
            linewidth=1,
            zorder=5,
        )
    )
    ax.text(
        0.025, titulo_y, "Drawdown máximo",
        transform=ax.transAxes, fontsize=8.5, fontweight="bold",
        va="top", ha="left", color=COR_TEXTO_PRIMARIO, zorder=6,
    )
    for i, (ticker, valor) in enumerate(minimos):
        ax.text(
            0.04, titulo_y - (i + 1) * passo,
            f"{NOMES[ticker]}   {valor:.1f}%",
            transform=ax.transAxes,
            fontsize=8.5,
            va="top",
            ha="left",
            color=CORES[ticker],
            fontweight="bold",
            zorder=6,
        )

    ax.axhline(0, color=COR_EIXO, linewidth=1)
    ax.set_title(
        "Drawdown — PETR4, VALE3, ITUB4 vs. IBOV (2 anos)",
        fontsize=13,
        color=COR_TEXTO_PRIMARIO,
        loc="left",
        fontweight="bold",
    )
    ax.set_ylabel("Drawdown (%)", color=COR_TEXTO_SECUNDARIO, fontsize=10)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))

    ax.grid(True, axis="y", color=COR_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COR_EIXO)

    ax.legend(
        loc="lower left",
        frameon=False,
        labelcolor=COR_TEXTO_SECUNDARIO,
        fontsize=9,
        ncol=4,
    )

    # Espaço extra abaixo para os rótulos do drawdown máximo
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - (ymax - ymin) * 0.08, ymax)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=150, facecolor=COR_SURFACE)
    print(f"Gráfico salvo em: {ARQUIVO_GRAFICO}")


if __name__ == "__main__":
    main()
