"""
Rutas de la API para el módulo de Empresas.

Endpoints:
    GET /empresas           → Listar / buscar empresas
    GET /empresas/{symbol}  → Detalle de una empresa
    GET /empresas/{symbol}/precios    → Precios históricos
    GET /empresas/{symbol}/noticias   → Noticias con sentimiento
    GET /empresas/{symbol}/financials → Datos financieros
    GET /empresas/{symbol}/balance    → Balance general
    GET /empresas/{symbol}/filings    → Presentaciones SEC
    GET /empresas/{symbol}/ejecutivos → Ejecutivos
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.schemas import (
    BalanceSchema,
    DatoFinancieroSchema,
    EjecutivoSchema,
    EmpresaDetalle,
    EmpresaResumen,
    FilingSchema,
    NoticiaSchema,
    PrecioSchema,
    PreciosResponse,
)
from backend.db.conexion import get_db
from backend.db.modelos import (
    BalanceGeneral,
    DatoFinanciero,
    Ejecutivo,
    Empresa,
    NoticiaSentimiento,
    PrecioHistorico,
    PresentacionSEC,
)

router = APIRouter(prefix="/empresas", tags=["Empresas"])


# ── LISTAR / BUSCAR ──────────────────────────────────────────────────────────


@router.get("/", response_model=list[EmpresaResumen])
def listar_empresas(
    sector: str | None = Query(None, description="Filtrar por sector"),
    industry: str | None = Query(None, description="Filtrar por industria"),
    search: str | None = Query(None, description="Buscar por nombre o símbolo"),
    order_by: str = Query("symbol", description="Ordenar por campo"),
    limit: int = Query(50, ge=1, le=500, description="Resultados por página"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: Session = Depends(get_db),
):
    """Lista empresas del S&P 500 con filtros opcionales."""
    query = db.query(Empresa)

    if sector:
        query = query.filter(Empresa.sector.ilike(f"%{sector}%"))
    if industry:
        query = query.filter(Empresa.industry.ilike(f"%{industry}%"))
    if search:
        query = query.filter(
            (Empresa.symbol.ilike(f"%{search}%"))
            | (Empresa.short_name.ilike(f"%{search}%"))
            | (Empresa.long_name.ilike(f"%{search}%"))
        )

    # Ordenamiento dinámico
    order_column = getattr(Empresa, order_by, Empresa.symbol)
    query = query.order_by(order_column)

    empresas = query.offset(offset).limit(limit).all()
    return empresas


# ── DETALLE ──────────────────────────────────────────────────────────────────


@router.get("/{symbol}", response_model=EmpresaDetalle)
def obtener_empresa(symbol: str, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de una empresa por su símbolo."""
    empresa = db.query(Empresa).filter(Empresa.symbol == symbol.upper()).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa '{symbol}' no encontrada")
    return empresa


# ── PRECIOS HISTÓRICOS ───────────────────────────────────────────────────────


@router.get("/{symbol}/precios", response_model=PreciosResponse)
def obtener_precios(
    symbol: str,
    desde: date | None = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: date | None = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    limit: int = Query(365, ge=1, le=5000, description="Máximo de registros"),
    db: Session = Depends(get_db),
):
    """Obtiene precios históricos OHLCV de un ticker."""
    sym = symbol.upper()

    # Verificar que la empresa existe
    empresa = db.query(Empresa).filter(Empresa.symbol == sym).first()
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa '{symbol}' no encontrada")

    query = db.query(PrecioHistorico).filter(PrecioHistorico.symbol == sym)

    if desde:
        query = query.filter(PrecioHistorico.date >= desde)
    else:
        # Por defecto, último año
        query = query.filter(PrecioHistorico.date >= date.today() - timedelta(days=365))

    if hasta:
        query = query.filter(PrecioHistorico.date <= hasta)

    precios = query.order_by(PrecioHistorico.date.desc()).limit(limit).all()

    return PreciosResponse(
        symbol=sym,
        count=len(precios),
        precios=[PrecioSchema.model_validate(p) for p in precios],
    )


# ── NOTICIAS ─────────────────────────────────────────────────────────────────


@router.get("/{symbol}/noticias", response_model=list[NoticiaSchema])
def obtener_noticias(
    symbol: str,
    sentiment: str | None = Query(None, description="Filtrar: positive/negative/neutral"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene noticias con sentimiento para un ticker."""
    sym = symbol.upper()
    query = db.query(NoticiaSentimiento).filter(NoticiaSentimiento.symbol == sym)

    if sentiment:
        query = query.filter(NoticiaSentimiento.lm_sentiment == sentiment.lower())

    noticias = query.limit(limit).all()
    return noticias


# ── DATOS FINANCIEROS ────────────────────────────────────────────────────────


@router.get("/{symbol}/financials", response_model=list[DatoFinancieroSchema])
def obtener_financials(
    symbol: str,
    item: str | None = Query(None, description="Filtrar por partida específica"),
    db: Session = Depends(get_db),
):
    """Obtiene datos financieros (ingresos, gastos, etc.) de un ticker."""
    sym = symbol.upper()
    query = db.query(DatoFinanciero).filter(DatoFinanciero.symbol == sym)

    if item:
        query = query.filter(DatoFinanciero.item.ilike(f"%{item}%"))

    return query.all()


# ── BALANCE GENERAL ──────────────────────────────────────────────────────────


@router.get("/{symbol}/balance", response_model=list[BalanceSchema])
def obtener_balance(
    symbol: str,
    item: str | None = Query(None, description="Filtrar por partida"),
    db: Session = Depends(get_db),
):
    """Obtiene partidas del balance general de un ticker."""
    sym = symbol.upper()
    query = db.query(BalanceGeneral).filter(BalanceGeneral.symbol == sym)

    if item:
        query = query.filter(BalanceGeneral.item.ilike(f"%{item}%"))

    return query.all()


# ── FILINGS SEC ──────────────────────────────────────────────────────────────


@router.get("/{symbol}/filings", response_model=list[FilingSchema])
def obtener_filings(
    symbol: str,
    filing_type: str | None = Query(None, description="Tipo: 8-K, 10-K, 10-Q"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Obtiene presentaciones SEC de un ticker."""
    sym = symbol.upper()
    query = db.query(PresentacionSEC).filter(PresentacionSEC.symbol == sym)

    if filing_type:
        query = query.filter(PresentacionSEC.filing_type == filing_type.upper())

    return query.limit(limit).all()


# ── EJECUTIVOS ───────────────────────────────────────────────────────────────


@router.get("/{symbol}/ejecutivos", response_model=list[EjecutivoSchema])
def obtener_ejecutivos(symbol: str, db: Session = Depends(get_db)):
    """Obtiene el equipo ejecutivo de un ticker."""
    sym = symbol.upper()
    return db.query(Ejecutivo).filter(Ejecutivo.symbol == sym).all()
