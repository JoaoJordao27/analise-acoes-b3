"""
Simula uma carteira com pesos iguais (1/3 cada) entre PETR4, VALE3 e ITUB4,
com rebalanceamento diário, e compara o retorno acumulado dela contra o IBOV.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

ARQUIVO_ENTRADA = "retornos_2anos.csv"
ARQUIVO_SAIDA = "carteira_vs_ibov.csv"
ARQUIVO_GRAFICO = "carteira_vs_ibov.png"

ATIVOS_CARTEIRA = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
PESO = 1 / 3
DIAS_UTEIS_ANO = 252

COR_CARTEIRA = "#4a3aa7"  # slot 7 - violet
COR_IBOV = "#eda100"      # slot 4 - yellow (mesma cor usada nos gráficos anteriores p/ IBOV)
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

    retornos_wide = df.pivot(index="Date", columns="Ticker", values="RetornoDiario")

    # Retorno diário da carteira: média simples dos 3 ativos (pesos iguais,
    # rebalanceada diariamente para 1/3 cada).
    retorno_carteira = retornos_wide[ATIVOS_CARTEIRA].mean(axis=1, skipna=False).dropna()
    retorno_ibov = retornos_wide["^BVSP"].dropna()

    datas_comuns = retorno_carteira.index.intersection(retorno_ibov.index)
    retorno_carteira = retorno_carteira.loc[datas_comuns].sort_index()
    retorno_ibov = retorno_ibov.loc[datas_comuns].sort_index()

    acumulado_carteira = (1 + retorno_carteira).cumprod() - 1
    acumulado_ibov = (1 + retorno_ibov).cumprod() - 1

    resultado = pd.DataFrame(
        {
            "RetornoDiarioCarteira": retorno_carteira,
            "RetornoAcumuladoCarteira": acumulado_carteira,
            "RetornoDiarioIBOV": retorno_ibov,
            "RetornoAcumuladoIBOV": acumulado_ibov,
        }
    )
    resultado.to_csv(ARQUIVO_SAIDA, encoding="utf-8")
    print(f"Série salva em: {ARQUIVO_SAIDA}\n")

    # Métricas de resumo
    indice_precos_carteira = (1 + retorno_carteira).cumprod()
    indice_precos_ibov = (1 + retorno_ibov).cumprod()

    resumo = pd.DataFrame(
        {
            "Carteira (1/3 PETR4+VALE3+ITUB4)": {
                "RetornoAcumulado(%)": acumulado_carteira.iloc[-1] * 100,
                "VolatilidadeAnualizada(%)": retorno_carteira.std() * (DIAS_UTEIS_ANO ** 0.5) * 100,
                "DrawdownMaximo(%)": calcular_drawdown(indice_precos_carteira).min() * 100,
            },
            "IBOV": {
                "RetornoAcumulado(%)": acumulado_ibov.iloc[-1] * 100,
                "VolatilidadeAnualizada(%)": retorno_ibov.std() * (DIAS_UTEIS_ANO ** 0.5) * 100,
                "DrawdownMaximo(%)": calcular_drawdown(indice_precos_ibov).min() * 100,
            },
        }
    ).T.round(2)
    print(resumo.to_string())

    # --- Gráfico ---
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COR_SURFACE)
    ax.set_facecolor(COR_SURFACE)

    ax.plot(
        resultado.index, resultado["RetornoAcumuladoCarteira"] * 100,
        color=COR_CARTEIRA, linewidth=2, solid_capstyle="round",
        label="Carteira (1/3 PETR4 + 1/3 VALE3 + 1/3 ITUB4)",
    )
    ax.plot(
        resultado.index, resultado["RetornoAcumuladoIBOV"] * 100,
        color=COR_IBOV, linewidth=2, solid_capstyle="round",
        label="IBOV",
    )

    for cor, coluna, nome in [
        (COR_CARTEIRA, "RetornoAcumuladoCarteira", "Carteira"),
        (COR_IBOV, "RetornoAcumuladoIBOV", "IBOV"),
    ]:
        ultimo_valor = resultado[coluna].iloc[-1] * 100
        ultima_data = resultado.index[-1]
        ax.annotate(
            f"{nome}  {ultimo_valor:+.1f}%",
            xy=(ultima_data, ultimo_valor),
            xytext=(6, 0), textcoords="offset points",
            va="center", fontsize=9.5, color=cor, fontweight="bold",
        )

    ax.axhline(0, color=COR_EIXO, linewidth=1)
    ax.set_title(
        "Carteira com pesos iguais (1/3 cada) vs. IBOV — retorno acumulado (2 anos)",
        fontsize=12.5, color=COR_TEXTO_PRIMARIO, loc="left", fontweight="bold",
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

    ax.legend(loc="upper left", frameon=False, labelcolor=COR_TEXTO_SECUNDARIO, fontsize=9)

    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin, xmax + (xmax - xmin) * 0.14)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=150, facecolor=COR_SURFACE)
    print(f"\nGráfico salvo em: {ARQUIVO_GRAFICO}")


if __name__ == "__main__":
    main()
