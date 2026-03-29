"""
Rutas de la API para vista de Mercado y Sectores.

Endpoints:
    GET /mercado/resumen   → Overview del S&P 500 completo
    GET /sectores          → Resumen agregado por sector
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.schemas import EmpresaResumen, MercadoResumen, SectorResumen
from backend.db.conexion import get_db
from backend.db.modelos import Empresa

router = APIRouter(tags=["Mercado"])


# ── SECTORES ─────────────────────────────────────────────────────────────────


@router.get("/sectores", response_model=list[SectorResumen])
def listar_sectores(db: Session = Depends(get_db)):
    """Resumen agregado de todos los sectores del S&P 500."""
    resultados = (
        db.query(
            Empresa.sector,
            func.count(Empresa.symbol).label("num_empresas"),
            func.sum(Empresa.market_cap).label("market_cap_total"),
            func.avg(Empresa.trailing_pe).label("avg_pe"),
            func.avg(Empresa.dividend_yield).label("avg_dividend_yield"),
            func.avg(Empresa.profit_margins).label("avg_profit_margin"),
        )
        .filter(Empresa.sector.isnot(None))
        .group_by(Empresa.sector)
        .order_by(func.sum(Empresa.market_cap).desc())
        .all()
    )

    return [
        SectorResumen(
            sector=r.sector,
            num_empresas=r.num_empresas,
            market_cap_total=int(r.market_cap_total) if r.market_cap_total else None,
            avg_pe=round(r.avg_pe, 2) if r.avg_pe else None,
            avg_dividend_yield=round(r.avg_dividend_yield, 4) if r.avg_dividend_yield else None,
            avg_profit_margin=round(r.avg_profit_margin, 4) if r.avg_profit_margin else None,
        )
        for r in resultados
    ]


# ── MERCADO RESUMEN ──────────────────────────────────────────────────────────


@router.get("/mercado/resumen", response_model=MercadoResumen)
def resumen_mercado(
    top_n: int = Query(5, ge=1, le=20, description="Número de top gainers/losers"),
    db: Session = Depends(get_db),
):
    """Vista general del mercado S&P 500: totales, top gainers/losers, sectores."""

    # Totales
    total_empresas = db.query(func.count(Empresa.symbol)).scalar()
    total_sectores = (
        db.query(func.count(func.distinct(Empresa.sector)))
        .filter(Empresa.sector.isnot(None))
        .scalar()
    )
    market_cap_total = db.query(func.sum(Empresa.market_cap)).scalar()
    avg_pe = db.query(func.avg(Empresa.trailing_pe)).scalar()

    # Top gainers (mayor revenue_growth)
    top_gainers = (
        db.query(Empresa)
        .filter(Empresa.revenue_growth.isnot(None))
        .order_by(Empresa.revenue_growth.desc())
        .limit(top_n)
        .all()
    )

    # Top losers (menor revenue_growth)
    top_losers = (
        db.query(Empresa)
        .filter(Empresa.revenue_growth.isnot(None))
        .order_by(Empresa.revenue_growth.asc())
        .limit(top_n)
        .all()
    )

    # Sectores (reutilizar lógica)
    sectores_raw = (
        db.query(
            Empresa.sector,
            func.count(Empresa.symbol).label("num_empresas"),
            func.sum(Empresa.market_cap).label("market_cap_total"),
            func.avg(Empresa.trailing_pe).label("avg_pe"),
            func.avg(Empresa.dividend_yield).label("avg_dividend_yield"),
            func.avg(Empresa.profit_margins).label("avg_profit_margin"),
        )
        .filter(Empresa.sector.isnot(None))
        .group_by(Empresa.sector)
        .order_by(func.sum(Empresa.market_cap).desc())
        .all()
    )

    sectores = [
        SectorResumen(
            sector=r.sector,
            num_empresas=r.num_empresas,
            market_cap_total=int(r.market_cap_total) if r.market_cap_total else None,
            avg_pe=round(r.avg_pe, 2) if r.avg_pe else None,
            avg_dividend_yield=round(r.avg_dividend_yield, 4) if r.avg_dividend_yield else None,
            avg_profit_margin=round(r.avg_profit_margin, 4) if r.avg_profit_margin else None,
        )
        for r in sectores_raw
    ]

    return MercadoResumen(
        total_empresas=total_empresas,
        total_sectores=total_sectores,
        market_cap_total=int(market_cap_total) if market_cap_total else None,
        avg_pe=round(avg_pe, 2) if avg_pe else None,
        top_gainers=[EmpresaResumen.model_validate(e) for e in top_gainers],
        top_losers=[EmpresaResumen.model_validate(e) for e in top_losers],
        sectores=sectores,
    )
