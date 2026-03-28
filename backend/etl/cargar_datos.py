"""
Pipeline ETL: Carga los CSVs del dataset de Kaggle a PostgreSQL (AWS RDS).

Uso:
    python -m backend.etl.cargar_datos          # Carga TODOS los CSVs
    python -m backend.etl.cargar_datos --solo precios   # Solo precios históricos

Pasos:
    1. Crea las tablas si no existen (CREATE IF NOT EXISTS)
    2. Limpia las tablas (TRUNCATE) para evitar duplicados
    3. Lee cada CSV con pandas
    4. Inserta los datos en lotes usando to_sql()
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# ── Imports del proyecto ──────────────────────────────────────────────────────
from backend.db.conexion import engine
from backend.db.modelos import Base

# ── Rutas de datos ────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ── Mapeo: archivo CSV → tabla de destino ────────────────────────────────────
MAPEO_CSV = {
    "01_company_info.csv": {
        "tabla": "empresas",
        "columnas_renombrar": {
            "industryKey": "industry_key",
            "sectorKey": "sector_key",
            "longBusinessSummary": "long_business_summary",
            "fullTimeEmployees": "full_time_employees",
            "auditRisk": "audit_risk",
            "boardRisk": "board_risk",
            "shareHolderRightsRisk": "shareholder_rights_risk",
            "overallRisk": "overall_risk",
            "dividendRate": "dividend_rate",
            "dividendYield": "dividend_yield",
            "exDividendDate": "ex_dividend_date",
            "payoutRatio": "payout_ratio",
            "fiveYearAvgDividendYield": "five_year_avg_dividend_yield",
            "trailingPE": "trailing_pe",
            "forwardPE": "forward_pe",
            "regularMarketVolume": "regular_market_volume",
            "averageVolume": "average_volume",
            "averageDailyVolume10Day": "average_daily_volume_10day",
            "marketCap": "market_cap",
            "fiftyTwoWeekLow": "fifty_two_week_low",
            "fiftyTwoWeekHigh": "fifty_two_week_high",
            "allTimeHigh": "all_time_high",
            "allTimeLow": "all_time_low",
            "priceToSalesTrailing12Months": "price_to_sales_trailing_12m",
            "fiftyDayAverage": "fifty_day_average",
            "twoHundredDayAverage": "two_hundred_day_average",
            "enterpriseValue": "enterprise_value",
            "profitMargins": "profit_margins",
            "floatShares": "float_shares",
            "sharesOutstanding": "shares_outstanding",
            "sharesShort": "shares_short",
            "heldPercentInsiders": "held_percent_insiders",
            "heldPercentInstitutions": "held_percent_institutions",
            "shortRatio": "short_ratio",
            "bookValue": "book_value",
            "priceToBook": "price_to_book",
            "trailingEps": "trailing_eps",
            "forwardEps": "forward_eps",
            "earningsQuarterlyGrowth": "earnings_quarterly_growth",
            "earningsGrowth": "earnings_growth",
            "revenueGrowth": "revenue_growth",
            "totalCash": "total_cash",
            "totalCashPerShare": "total_cash_per_share",
            "totalDebt": "total_debt",
            "totalRevenue": "total_revenue",
            "debtToEquity": "debt_to_equity",
            "quickRatio": "quick_ratio",
            "currentRatio": "current_ratio",
            "revenuePerShare": "revenue_per_share",
            "returnOnAssets": "return_on_assets",
            "returnOnEquity": "return_on_equity",
            # grossProfits se omite — dato agregado, no está en el modelo
            "freeCashflow": "free_cashflow",
            "operatingCashflow": "operating_cashflow",
            "grossMargins": "gross_margins",
            "ebitdaMargins": "ebitda_margins",
            "operatingMargins": "operating_margins",
            "financialCurrency": "financial_currency",
            "quoteType": "quote_type",
            "currentPrice": "current_price",
            "recommendationKey": "recommendation_key",
            "numberOfAnalystOpinions": "number_of_analyst_opinions",
            "shortName": "short_name",
            "longName": "long_name",
        },
    },
    "02_company_news_sentiment.csv": {
        "tabla": "noticias_sentimiento",
        "columnas_renombrar": {
            "pubDate": "pub_date",
            "lm_level": "lm_level",
            "lm_score1": "lm_score1",
            "lm_score2": "lm_score2",
            "lm_sentiment": "lm_sentiment",
        },
    },
    "03_company_balance_sheet.csv": {
        "tabla": "balance_general",
        "columnas_renombrar": {"Symbol": "symbol", "Item": "item", "Period": "period", "Value": "value"},
    },
    "04_company_financials.csv": {
        "tabla": "datos_financieros",
        "columnas_renombrar": {"Symbol": "symbol", "Item": "item", "Period": "period", "Value": "value"},
    },
    "05_company_filings.csv": {
        "tabla": "presentaciones_sec",
        "columnas_renombrar": {"filing_date": "filing_date", "filing_type": "filing_type", "edgarUrl": "edgar_url"},
    },
    "06_company_officers.csv": {
        "tabla": "ejecutivos",
        "columnas_renombrar": {"totalPay": "total_pay"},
    },
}


def _log(msg: str) -> None:
    """Imprime con timestamp."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def crear_tablas() -> None:
    """Crea todas las tablas si no existen."""
    _log("Creando tablas (si no existen)...")
    Base.metadata.create_all(bind=engine)
    _log("✅ Tablas listas")


def cargar_csv(archivo: str, config: dict) -> int:
    """Carga un CSV individual a su tabla de destino.

    Returns:
        Número de filas insertadas.
    """
    ruta = DATA_DIR / archivo
    tabla = config["tabla"]
    renombrar = config.get("columnas_renombrar", {})

    _log(f"  📄 Leyendo {archivo}...")
    df = pd.read_csv(ruta, low_memory=False)

    # Renombrar columnas camelCase → snake_case
    if renombrar:
        df = df.rename(columns=renombrar)

    # Quedarse solo con columnas que existen en el modelo
    with engine.connect() as conn:
        columnas_tabla = [
            row[0]
            for row in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    f"WHERE table_name = '{tabla}'"
                )
            )
        ]

    # Filtrar columnas del DataFrame que no existen en la tabla
    columnas_validas = [c for c in df.columns if c.lower() in columnas_tabla]
    df = df[[c for c in df.columns if c.lower() in columnas_tabla]]
    df.columns = [c.lower() for c in df.columns]

    # Eliminar columna 'id' si existe (es autoincremental)
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    _log(f"  📦 Insertando {len(df):,} filas en '{tabla}'...")

    # Truncar tabla antes de insertar
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {tabla} RESTART IDENTITY CASCADE"))

    # Insertar en lotes
    df.to_sql(tabla, engine, if_exists="append", index=False, chunksize=5000)

    _log(f"  ✅ {len(df):,} filas → '{tabla}'")
    return len(df)


def cargar_precios() -> int:
    """Carga todos los CSVs de price_data/ en la tabla precios_historicos."""
    price_dir = DATA_DIR / "price_data"
    archivos = sorted(price_dir.glob("*.csv"))

    _log(f"  📈 Encontrados {len(archivos)} archivos de precios")

    # Truncar tabla
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE precios_historicos RESTART IDENTITY CASCADE"))

    total = 0
    for i, archivo in enumerate(archivos, 1):
        df = pd.read_csv(archivo)
        df.columns = [c.lower() for c in df.columns]

        # Asegurar que 'date' sea tipo fecha
        df["date"] = pd.to_datetime(df["date"]).dt.date

        df.to_sql("precios_historicos", engine, if_exists="append", index=False, chunksize=5000)
        total += len(df)

        if i % 50 == 0 or i == len(archivos):
            _log(f"    Progreso: {i}/{len(archivos)} tickers ({total:,} filas)")

    _log(f"  ✅ {total:,} filas → 'precios_historicos'")
    return total


def main(solo: str | None = None) -> None:
    """Ejecuta el pipeline ETL completo.

    Args:
        solo: Si se especifica, carga solo ese grupo ("precios" o "info").
    """
    inicio = time.time()
    _log("═" * 60)
    _log("🚀 MarketSense ETL — Inicio de carga")
    _log("═" * 60)

    # Paso 1: Crear tablas
    crear_tablas()

    total_filas = 0

    if solo != "precios":
        # Paso 2: Cargar CSVs principales
        _log("")
        _log("── CARGANDO CSVs PRINCIPALES ──")
        for archivo, config in MAPEO_CSV.items():
            try:
                filas = cargar_csv(archivo, config)
                total_filas += filas
            except Exception as e:
                _log(f"  ❌ Error en {archivo}: {e}")

    if solo != "info":
        # Paso 3: Cargar precios históricos
        _log("")
        _log("── CARGANDO PRECIOS HISTÓRICOS ──")
        try:
            filas = cargar_precios()
            total_filas += filas
        except Exception as e:
            _log(f"  ❌ Error en precios: {e}")

    duracion = time.time() - inicio
    _log("")
    _log("═" * 60)
    _log(f"🏁 ETL completado en {duracion:.1f}s — {total_filas:,} filas totales")
    _log("═" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MarketSense ETL")
    parser.add_argument(
        "--solo",
        choices=["precios", "info"],
        default=None,
        help="Cargar solo un subconjunto: 'precios' o 'info'",
    )
    args = parser.parse_args()
    main(solo=args.solo)
