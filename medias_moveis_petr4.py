"""
Calcula as médias móveis de 20 e 50 dias do preço de PETR4, identifica os
cruzamentos (golden cross / death cross) e plota tudo junto com o preço.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

ARQUIVO_ENTRADA = "cotacoes_2anos.csv"
ARQUIVO_SAIDA_CRUZAMENTOS = "cruzamentos_petr4.csv"
ARQUIVO_GRAFICO = "medias_moveis_petr4.png"

TICKER = "PETR4.SA"
JANELA_CURTA = 20
JANELA_LONGA = 50

# Paleta do skill dataviz
COR_PRECO = "#898781"       # ink muted - o preço é o pano de fundo, não a identidade
COR_SMA_CURTA = "#2a78d6"   # slot 1 - blue
COR_SMA_LONGA = "#eb6834"   # slot 2 - orange
COR_GOLDEN = "#0ca30c"      # status "good"
COR_DEATH = "#d03b3b"       # status "critical"
COR_GRID = "#e1e0d9"
COR_EIXO = "#c3c2b7"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_SURFACE = "#fcfcfb"


def calcular_medias_e_cruzamentos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("Date").copy()
    df["SMA20"] = df["Close"].rolling(JANELA_CURTA).mean()
    df["SMA50"] = df["Close"].rolling(JANELA_LONGA).mean()

    diferenca = df["SMA20"] - df["SMA50"]
    sinal = diferenca.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    mudanca = sinal.diff()

    df["Cruzamento"] = None
    df.loc[mudanca == 2, "Cruzamento"] = "Golden Cross"
    df.loc[mudanca == -2, "Cruzamento"] = "Death Cross"
    return df


def main():
    df_todos = pd.read_csv(ARQUIVO_ENTRADA, parse_dates=["Date"])
    df = df_todos[df_todos["Ticker"] == TICKER].copy()
    df = calcular_medias_e_cruzamentos(df)

    cruzamentos = df[df["Cruzamento"].notna()][["Date", "Close", "SMA20", "SMA50", "Cruzamento"]]
    cruzamentos.to_csv(ARQUIVO_SAIDA_CRUZAMENTOS, index=False, encoding="utf-8")
    print(f"Cruzamentos salvos em: {ARQUIVO_SAIDA_CRUZAMENTOS}\n")
    print(cruzamentos.to_string(index=False))

    fig, ax = plt.subplots(figsize=(11, 6), facecolor=COR_SURFACE)
    ax.set_facecolor(COR_SURFACE)

    ax.plot(df["Date"], df["Close"], color=COR_PRECO, linewidth=1.2, label="Preço (fechamento)", zorder=2)
    ax.plot(df["Date"], df["SMA20"], color=COR_SMA_CURTA, linewidth=1.8, label=f"Média móvel {JANELA_CURTA}d", zorder=3)
    ax.plot(df["Date"], df["SMA50"], color=COR_SMA_LONGA, linewidth=1.8, label=f"Média móvel {JANELA_LONGA}d", zorder=3)

    golden = cruzamentos[cruzamentos["Cruzamento"] == "Golden Cross"]
    death = cruzamentos[cruzamentos["Cruzamento"] == "Death Cross"]

    ax.scatter(
        golden["Date"], golden["Close"], marker="^", s=140,
        color=COR_GOLDEN, edgecolor=COR_SURFACE, linewidth=1.2, zorder=5, label="Golden Cross",
    )
    ax.scatter(
        death["Date"], death["Close"], marker="v", s=140,
        color=COR_DEATH, edgecolor=COR_SURFACE, linewidth=1.2, zorder=5, label="Death Cross",
    )

    # Rótulo direto (texto) em cada cruzamento, alternando acima/abaixo do
    # marcador para reduzir chance de colisão com a série de preço.
    for _, linha in golden.iterrows():
        ax.annotate(
            f"Golden Cross\n{linha['Date'].strftime('%d/%m/%y')}",
            xy=(linha["Date"], linha["Close"]),
            xytext=(0, 14), textcoords="offset points",
            ha="center", va="bottom", fontsize=8, color=COR_GOLDEN, fontweight="bold",
        )
    for _, linha in death.iterrows():
        ax.annotate(
            f"Death Cross\n{linha['Date'].strftime('%d/%m/%y')}",
            xy=(linha["Date"], linha["Close"]),
            xytext=(0, -14), textcoords="offset points",
            ha="center", va="top", fontsize=8, color=COR_DEATH, fontweight="bold",
        )

    ax.set_title(
        f"PETR4 — Preço e médias móveis ({JANELA_CURTA}d / {JANELA_LONGA}d)",
        fontsize=13, color=COR_TEXTO_PRIMARIO, loc="left", fontweight="bold",
    )
    ax.set_ylabel("Preço (R$)", color=COR_TEXTO_SECUNDARIO, fontsize=10)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))

    ax.grid(True, axis="y", color=COR_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COR_EIXO)

    ax.legend(loc="upper left", frameon=False, labelcolor=COR_TEXTO_SECUNDARIO, fontsize=9, ncol=2)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=150, facecolor=COR_SURFACE)
    print(f"\nGráfico salvo em: {ARQUIVO_GRAFICO}")


if __name__ == "__main__":
    main()
