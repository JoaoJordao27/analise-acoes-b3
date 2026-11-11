"""
Baixa os últimos 2 anos de cotações diárias de PETR4.SA, VALE3.SA, ITUB4.SA e ^BVSP
usando yfinance e salva o resultado em um CSV.
"""

import yfinance as yf
import pandas as pd

TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"]
PERIODO = "2y"
INTERVALO = "1d"
ARQUIVO_SAIDA = "cotacoes_2anos.csv"


def main():
    print(f"Baixando dados de {TICKERS} (período={PERIODO}, intervalo={INTERVALO})...")

    dados = yf.download(
        TICKERS,
        period=PERIODO,
        interval=INTERVALO,
        auto_adjust=True,
        group_by="ticker",
        progress=False,
    )

    if dados.empty:
        raise SystemExit("Nenhum dado foi retornado pelo yfinance. Verifique sua conexão ou os tickers.")

    # Reorganiza para formato "longo": Date, Ticker, Open, High, Low, Close, Volume
    linhas = []
    for ticker in TICKERS:
        df_ticker = dados[ticker].copy()
        df_ticker = df_ticker.dropna(how="all")
        df_ticker["Ticker"] = ticker
        df_ticker = df_ticker.reset_index()
        linhas.append(df_ticker)

    df_final = pd.concat(linhas, ignore_index=True)
    df_final = df_final[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
    df_final = df_final.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")
    print(f"Salvo em: {ARQUIVO_SAIDA}")
    print(f"Total de linhas: {len(df_final)}")
    print(df_final.groupby("Ticker")["Date"].agg(["min", "max", "count"]))


if __name__ == "__main__":
    main()
