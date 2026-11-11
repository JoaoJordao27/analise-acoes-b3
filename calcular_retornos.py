"""
Calcula o retorno diário e o retorno acumulado de cada ativo a partir de
cotacoes_2anos.csv, salva o resultado em CSV e plota um gráfico comparando
os 4 ativos.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

ARQUIVO_ENTRADA = "cotacoes_2anos.csv"
ARQUIVO_SAIDA = "retornos_2anos.csv"
ARQUIVO_GRAFICO = "retorno_acumulado.png"

# Paleta categórica validada (ordem fixa, slots 1-4 do padrão do skill dataviz)
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

# Cores de apoio (paleta do skill dataviz)
COR_GRID = "#e1e0d9"
COR_EIXO = "#c3c2b7"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_SURFACE = "#fcfcfb"


def calcular_retornos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["Ticker", "Date"]).copy()
    df["RetornoDiario"] = df.groupby("Ticker")["Close"].pct_change()
    df["RetornoAcumulado"] = (
        df.groupby("Ticker")["RetornoDiario"]
        .apply(lambda s: (1 + s.fillna(0)).cumprod() - 1)
        .reset_index(level=0, drop=True)
    )
    return df


def plotar(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COR_SURFACE)
    ax.set_facecolor(COR_SURFACE)

    ordem = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"]

    for ticker in ordem:
        serie = df[df["Ticker"] == ticker]
        ax.plot(
            serie["Date"],
            serie["RetornoAcumulado"] * 100,
            label=NOMES[ticker],
            color=CORES[ticker],
            linewidth=2,
            solid_capstyle="round",
        )

    # Rótulos diretos no fim de cada linha, com afastamento vertical mínimo
    # para não colidir quando dois retornos finais ficam próximos.
    finais = []
    for ticker in ordem:
        serie = df[df["Ticker"] == ticker]
        ultimo = serie.iloc[-1]
        finais.append((ticker, ultimo["Date"], ultimo["RetornoAcumulado"] * 100))

    ymin, ymax = ax.get_ylim()
    espacamento_minimo = (ymax - ymin) * 0.045
    finais.sort(key=lambda t: t[2])
    for i in range(1, len(finais)):
        _, data_i, valor_i = finais[i]
        _, data_anterior, valor_anterior = finais[i - 1]
        if valor_i - valor_anterior < espacamento_minimo:
            finais[i] = (finais[i][0], finais[i][1], valor_anterior + espacamento_minimo)

    for ticker, data_x, y_rotulo in finais:
        valor_real = df.loc[df["Ticker"] == ticker, "RetornoAcumulado"].iloc[-1] * 100
        ax.annotate(
            f"{NOMES[ticker]}  {valor_real:+.1f}%",
            xy=(data_x, y_rotulo),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=CORES[ticker],
            fontweight="bold",
        )

    ax.axhline(0, color=COR_EIXO, linewidth=1)
    ax.set_title(
        "Retorno acumulado — PETR4, VALE3, ITUB4 vs. IBOV (2 anos)",
        fontsize=13,
        color=COR_TEXTO_PRIMARIO,
        loc="left",
        fontweight="bold",
    )
    ax.set_ylabel("Retorno acumulado (%)", color=COR_TEXTO_SECUNDARIO, fontsize=10)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))

    ax.grid(True, axis="y", color=COR_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COR_EIXO)

    ax.legend(
        loc="upper left",
        frameon=False,
        labelcolor=COR_TEXTO_SECUNDARIO,
        fontsize=9,
    )

    # Espaço extra à direita para os rótulos diretos
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin, xmax + (xmax - xmin) * 0.12)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=150, facecolor=COR_SURFACE)
    print(f"Gráfico salvo em: {ARQUIVO_GRAFICO}")


def main():
    df = pd.read_csv(ARQUIVO_ENTRADA, parse_dates=["Date"])
    df = calcular_retornos(df)

    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")
    print(f"Retornos salvos em: {ARQUIVO_SAIDA}")

    resumo = df.groupby("Ticker").agg(
        RetornoAcumuladoFinal=("RetornoAcumulado", "last"),
        RetornoDiarioMedio=("RetornoDiario", "mean"),
        VolatilidadeDiaria=("RetornoDiario", "std"),
    )
    resumo["RetornoAcumuladoFinal"] = (resumo["RetornoAcumuladoFinal"] * 100).round(2)
    resumo["RetornoDiarioMedio"] = (resumo["RetornoDiarioMedio"] * 100).round(3)
    resumo["VolatilidadeDiaria"] = (resumo["VolatilidadeDiaria"] * 100).round(3)
    print("\nResumo (%):")
    print(resumo)

    plotar(df)


if __name__ == "__main__":
    main()
