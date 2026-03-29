"""Esquemas Pydantic para las respuestas de la API MarketSense."""

from datetime import date

from pydantic import BaseModel, ConfigDict

# ═══════════════════════════════════════════════════════════════════════════════
# EMPRESA
# ═══════════════════════════════════════════════════════════════════════════════


class EmpresaResumen(BaseModel):
    """Resumen breve de una empresa (para listados)."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    short_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    current_price: float | None = None
    market_cap: int | None = None
    country: str | None = None


class EmpresaDetalle(BaseModel):
    """Detalle completo de una empresa."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str

    # Identificación
    short_name: str | None = None
    long_name: str | None = None
    website: str | None = None
    long_business_summary: str | None = None

    # Ubicación
    address: str | None = None
    city: str | None = None
    country: str | None = None

    # Clasificación
    sector: str | None = None
    industry: str | None = None
    full_time_employees: int | None = None

    # Precios
    current_price: float | None = None
    fifty_two_week_low: float | None = None
    fifty_two_week_high: float | None = None
    fifty_day_average: float | None = None
    two_hundred_day_average: float | None = None

    # Valoración
    market_cap: int | None = None
    enterprise_value: int | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None
    beta: float | None = None

    # Dividendos
    dividend_rate: float | None = None
    dividend_yield: float | None = None

    # Rentabilidad
    profit_margins: float | None = None
    return_on_equity: float | None = None
    return_on_assets: float | None = None
    gross_margins: float | None = None
    operating_margins: float | None = None

    # Earnings
    trailing_eps: float | None = None
    forward_eps: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None

    # Deuda y Cash
    total_cash: int | None = None
    total_debt: int | None = None
    total_revenue: int | None = None
    debt_to_equity: float | None = None
    free_cashflow: int | None = None

    # Volumen
    average_volume: int | None = None

    # Recomendación
    recommendation_key: str | None = None
    number_of_analyst_opinions: int | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# PRECIOS
# ═══════════════════════════════════════════════════════════════════════════════


class PrecioSchema(BaseModel):
    """Un punto de datos de precio diario OHLCV."""

    model_config = ConfigDict(from_attributes=True)

    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None


class PreciosResponse(BaseModel):
    """Respuesta con precios históricos de un ticker."""

    symbol: str
    count: int
    precios: list[PrecioSchema]


# ═══════════════════════════════════════════════════════════════════════════════
# NOTICIAS
# ═══════════════════════════════════════════════════════════════════════════════


class NoticiaSchema(BaseModel):
    """Noticia con análisis de sentimiento."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    title: str | None = None
    summary: str | None = None
    provider: str | None = None
    pub_date: str | None = None
    url: str | None = None
    lm_sentiment: str | None = None
    lm_score1: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# FINANCIEROS
# ═══════════════════════════════════════════════════════════════════════════════


class DatoFinancieroSchema(BaseModel):
    """Partida financiera individual."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    item: str
    period: str
    value: float | None = None


class BalanceSchema(BaseModel):
    """Partida del balance general."""

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    item: str
    period: str
    value: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# SEC FILINGS
# ═══════════════════════════════════════════════════════════════════════════════


class FilingSchema(BaseModel):
    """Presentación ante la SEC."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    filing_date: str | None = None
    filing_type: str | None = None
    title: str | None = None
    edgar_url: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# EJECUTIVOS
# ═══════════════════════════════════════════════════════════════════════════════


class EjecutivoSchema(BaseModel):
    """Ejecutivo de una empresa."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    title: str | None = None
    age: float | None = None
    total_pay: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR / MERCADO
# ═══════════════════════════════════════════════════════════════════════════════


class SectorResumen(BaseModel):
    """Resumen agregado de un sector."""

    sector: str
    num_empresas: int
    market_cap_total: int | None = None
    avg_pe: float | None = None
    avg_dividend_yield: float | None = None
    avg_profit_margin: float | None = None


class MercadoResumen(BaseModel):
    """Vista general del mercado S&P 500."""

    total_empresas: int
    total_sectores: int
    market_cap_total: int | None = None
    avg_pe: float | None = None
    top_gainers: list[EmpresaResumen]
    top_losers: list[EmpresaResumen]
    sectores: list[SectorResumen]


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT / AGENTE
# ═══════════════════════════════════════════════════════════════════════════════


class ChatRequest(BaseModel):
    """Petición de chat al agente."""

    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Respuesta del agente."""

    response: str
    conversation_id: str
    sources: list[str] = []


# ═══════════════════════════════════════════════════════════════════════════════
# PAGINACIÓN
# ═══════════════════════════════════════════════════════════════════════════════


class PaginatedResponse(BaseModel):
    """Wrapper genérico para respuestas paginadas."""

    total: int
    page: int
    per_page: int
    items: list
