"""
Modelos SQLAlchemy para la base de datos MarketSense.

Tablas:
  - empresas                → Información de las 500+ empresas del S&P 500
  - noticias_sentimiento    → Noticias con análisis de sentimiento
  - balance_general         → Partidas del balance general (formato largo)
  - datos_financieros       → Partidas financieras: ingresos, gastos, etc.
  - presentaciones_sec      → Filings ante la SEC (8-K, 10-K, etc.)
  - ejecutivos              → Oficiales y ejecutivos de cada empresa
  - precios_historicos      → Precios diarios OHLCV para cada ticker
"""

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base para todos los modelos."""
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INFORMACIÓN DE EMPRESAS  (01_company_info.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class Empresa(Base):
    """Datos maestros de cada empresa del S&P 500."""

    __tablename__ = "empresas"

    symbol = Column(String(10), primary_key=True, comment="Ticker (ej: AAPL)")

    # ── Ubicación ─────────────────────────────────────────────────────────────
    address = Column(String(255))
    city = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100))
    phone = Column(String(50))
    website = Column(String(255))

    # ── Clasificación ─────────────────────────────────────────────────────────
    industry = Column(String(200))
    industry_key = Column(String(100))
    sector = Column(String(100))
    sector_key = Column(String(100))
    long_business_summary = Column(Text)

    # ── Empleados y gobernanza ────────────────────────────────────────────────
    full_time_employees = Column(BigInteger)
    audit_risk = Column(Integer)
    board_risk = Column(Integer)
    shareholder_rights_risk = Column(Integer)
    overall_risk = Column(Integer)

    # ── Dividendos ────────────────────────────────────────────────────────────
    dividend_rate = Column(Float)
    dividend_yield = Column(Float)
    ex_dividend_date = Column(String(50))
    payout_ratio = Column(Float)
    five_year_avg_dividend_yield = Column(Float)

    # ── Valoración ────────────────────────────────────────────────────────────
    beta = Column(Float)
    trailing_pe = Column(Float)
    forward_pe = Column(Float)
    market_cap = Column(BigInteger)
    enterprise_value = Column(BigInteger)
    price_to_book = Column(Float)
    price_to_sales_trailing_12m = Column(Float)
    book_value = Column(Float)

    # ── Precios ───────────────────────────────────────────────────────────────
    current_price = Column(Float)
    fifty_two_week_low = Column(Float)
    fifty_two_week_high = Column(Float)
    all_time_high = Column(Float)
    all_time_low = Column(Float)
    fifty_day_average = Column(Float)
    two_hundred_day_average = Column(Float)

    # ── Volumen ───────────────────────────────────────────────────────────────
    regular_market_volume = Column(BigInteger)
    average_volume = Column(BigInteger)
    average_daily_volume_10day = Column(BigInteger)

    # ── Rentabilidad ──────────────────────────────────────────────────────────
    profit_margins = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)
    gross_margins = Column(Float)
    ebitda_margins = Column(Float)
    operating_margins = Column(Float)

    # ── Earnings ──────────────────────────────────────────────────────────────
    trailing_eps = Column(Float)
    forward_eps = Column(Float)
    earnings_quarterly_growth = Column(Float)
    earnings_growth = Column(Float)
    revenue_growth = Column(Float)

    # ── Cash y deuda ──────────────────────────────────────────────────────────
    total_cash = Column(BigInteger)
    total_cash_per_share = Column(Float)
    ebitda = Column(BigInteger)
    total_debt = Column(BigInteger)
    total_revenue = Column(BigInteger)
    debt_to_equity = Column(Float)
    quick_ratio = Column(Float)
    current_ratio = Column(Float)
    revenue_per_share = Column(Float)
    free_cashflow = Column(BigInteger)
    operating_cashflow = Column(BigInteger)

    # ── Shares ────────────────────────────────────────────────────────────────
    float_shares = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    shares_short = Column(BigInteger)
    held_percent_insiders = Column(Float)
    held_percent_institutions = Column(Float)
    short_ratio = Column(Float)

    # ── Metadata ──────────────────────────────────────────────────────────────
    currency = Column(String(10))
    financial_currency = Column(String(10))
    exchange = Column(String(20))
    quote_type = Column(String(20))
    short_name = Column(String(200))
    long_name = Column(String(300))
    recommendation_key = Column(String(50))
    number_of_analyst_opinions = Column(Integer)

    def __repr__(self):
        return f"<Empresa {self.symbol}: {self.short_name}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NOTICIAS CON SENTIMIENTO  (02_company_news_sentiment.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class NoticiaSentimiento(Base):
    """Noticias financieras con scores de sentimiento (Loughran-McDonald)."""

    __tablename__ = "noticias_sentimiento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    title = Column(Text)
    summary = Column(Text)
    provider = Column(String(100))
    pub_date = Column(String(50))
    thumbnail = Column(Text)
    url = Column(Text)

    # ── Sentimiento (Loughran-McDonald) ───────────────────────────────────────
    lm_level = Column(Integer, comment="Nivel de sentimiento (-5 a +5)")
    lm_score1 = Column(Float, comment="Score primario normalizado")
    lm_score2 = Column(Float, comment="Score secundario normalizado")
    lm_sentiment = Column(String(20), comment="positive / negative / neutral")

    def __repr__(self):
        return f"<Noticia {self.symbol}: {self.title[:50]}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. BALANCE GENERAL  (03_company_balance_sheet.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class BalanceGeneral(Base):
    """Partidas del balance general en formato largo (Symbol, Item, Period, Value)."""

    __tablename__ = "balance_general"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    item = Column(String(200), nullable=False, comment="Nombre de la partida contable")
    period = Column(String(20), nullable=False, comment="Fecha del periodo fiscal")
    value = Column(Float, comment="Valor numérico de la partida")

    def __repr__(self):
        return f"<Balance {self.symbol} | {self.item} | {self.period}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. DATOS FINANCIEROS  (04_company_financials.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class DatoFinanciero(Base):
    """Datos financieros: ingresos, gastos, impuestos (formato largo)."""

    __tablename__ = "datos_financieros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    item = Column(String(200), nullable=False)
    period = Column(String(20), nullable=False)
    value = Column(Float)

    def __repr__(self):
        return f"<Financiero {self.symbol} | {self.item} | {self.period}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PRESENTACIONES SEC  (05_company_filings.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class PresentacionSEC(Base):
    """Filings ante la SEC (8-K, 10-K, 10-Q, etc.)."""

    __tablename__ = "presentaciones_sec"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    filing_date = Column(String(20))
    filing_type = Column(String(20))
    title = Column(Text)
    edgar_url = Column(Text)

    def __repr__(self):
        return f"<Filing {self.symbol}: {self.filing_type} {self.filing_date}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. EJECUTIVOS  (06_company_officers.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class Ejecutivo(Base):
    """Oficiales y ejecutivos de cada empresa del S&P 500."""

    __tablename__ = "ejecutivos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    name = Column(String(200))
    age = Column(Float)
    title = Column(String(300))
    total_pay = Column(Float)

    def __repr__(self):
        return f"<Ejecutivo {self.symbol}: {self.name}>"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PRECIOS HISTÓRICOS  (price_data/*.csv)
# ═══════════════════════════════════════════════════════════════════════════════

class PrecioHistorico(Base):
    """Precios diarios OHLCV — 15 años de historial por ticker."""

    __tablename__ = "precios_historicos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    def __repr__(self):
        return f"<Precio {self.symbol} {self.date}: {self.close}>"
