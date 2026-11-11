"""
Calcula, para cada ativo, a volatilidade anualizada (desvio padrão dos
retornos diários) e o drawdown máximo, a partir de retornos_2anos.csv.
"""

import pandas as pd

ARQUIVO_ENTRADA = "retornos_2anos.csv"
ARQUIVO_SAIDA = "risco_2anos.csv"
DIAS_UTEIS_ANO = 252

NOMES = {
    "PETR4.SA": "PETR4",
    "VALE3.SA": "VALE3",
    "ITUB4.SA": "ITUB4",
    "^BVSP": "IBOV",
}


def calcular_drawdown(precos: pd.Series) -> pd.Series:
    pico = precos.cummax()
    return precos / pico - 1


def main():
    df = pd.read_csv(ARQUIVO_ENTRADA, parse_dates=["Date"])
    df = df.sort_values(["Ticker", "Date"])

    resultados = []
    for ticker, grupo in df.groupby("Ticker"):
        grupo = grupo.sort_values("Date")

        vol_diaria = grupo["RetornoDiario"].std()
        vol_anualizada = vol_diaria * (DIAS_UTEIS_ANO ** 0.5)

        drawdown = calcular_drawdown(grupo["Close"])
        drawdown_maximo = drawdown.min()
        data_fundo = grupo.loc[drawdown.idxmin(), "Date"]
        # Data do pico anterior ao fundo do drawdown máximo
        pico_precos = grupo["Close"].cummax()
        data_pico = grupo.loc[
            grupo.index[grupo["Close"] == pico_precos.loc[drawdown.idxmin()]].max(), "Date"
        ]

        resultados.append(
            {
                "Ticker": ticker,
                "Ativo": NOMES.get(ticker, ticker),
                "VolatilidadeDiaria(%)": round(vol_diaria * 100, 3),
                "VolatilidadeAnualizada(%)": round(vol_anualizada * 100, 2),
                "DrawdownMaximo(%)": round(drawdown_maximo * 100, 2),
                "DataPico": data_pico.date(),
                "DataFundo": data_fundo.date(),
            }
        )

    resumo = pd.DataFrame(resultados).sort_values("VolatilidadeAnualizada(%)", ascending=False)
    resumo.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")

    print(f"Resultado salvo em: {ARQUIVO_SAIDA}\n")
    print(resumo.to_string(index=False))


if __name__ == "__main__":
    main()
