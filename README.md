# 🧠 MarketSense

**Plataforma de agentes inteligentes para análisis financiero**, potenciada por LLMs de AWS Bedrock y orquestada con LangGraph.

MarketSense no es un chatbot genérico — es un **analista experto** capaz de consultar bases de datos SQL, buscar noticias financieras en tiempo real y ejecutar código para generar reportes precisos del S&P 500.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│              Dashboard financiero interactivo                │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────┐     │
│  │            LangGraph Agent Orchestrator              │     │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │     │
│  │  │ SQL Tool │  │News Tool │  │ Code Exec Tool    │  │     │
│  │  └────┬─────┘  └────┬─────┘  └───────┬───────────┘  │     │
│  └───────┼──────────────┼────────────────┼──────────────┘     │
│          │              │                │                     │
│    ┌─────▼─────┐  ┌─────▼─────┐  ┌──────▼──────┐             │
│    │ RDS (SQL) │  │ News APIs │  │ Sandbox Env │             │
│    └───────────┘  └───────────┘  └─────────────┘             │
│                                                               │
│    ┌─────────────────────────────────────────────┐            │
│    │        RAG Pipeline (FAISS + Embeddings)     │            │
│    └─────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  AWS Bedrock    │
              │  (Claude 3.5)   │
              └─────────────────┘
```

---

## 📂 Estructura del Proyecto

```
├── backend/          # Código Python principal
│   ├── agents/       # Agentes LangGraph
│   ├── tools/        # Tools: SQL, búsqueda, ejecución de código
│   ├── etl/          # Pipelines de ingesta de datos (S&P 500)
│   ├── rag/          # Retrieval-Augmented Generation
│   ├── db/           # Modelos SQLAlchemy y conexión a RDS
│   └── api/          # API FastAPI
├── frontend/         # App Next.js (dashboard)
├── notebooks/        # Jupyter notebooks de exploración
├── tests/            # Tests unitarios e integración
└── infra/            # Infraestructura (Docker, IaC)
```

---

## 🚀 Quick Start

### Prerrequisitos

- Python 3.10+
- Node.js 18+
- AWS Account con acceso a Bedrock

### 1. Clonar y configurar entorno

```bash
git clone <repo-url>
cd IA-Generativa

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Instalar dependencias

```bash
# Backend (Python)
make install

# Frontend (Next.js)
make install-frontend
```

### 3. Desarrollo

```bash
# Backend
make dev-backend

# Frontend (en otra terminal)
make dev-frontend

# Jupyter notebooks
make notebook
```

### 4. Calidad de código

```bash
make lint    # Linter + formatter (ruff)
make test    # Tests (pytest)
```

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| LLM | AWS Bedrock (Claude 3.5 Sonnet) |
| Orquestación | LangGraph 1.1 + LangChain 1.2 |
| Backend API | FastAPI + Uvicorn |
| Base de Datos | PostgreSQL (AWS RDS) + SQLAlchemy 2.0 |
| RAG | FAISS + Embeddings |
| ETL | Python + Pandas + yfinance |
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Testing | Pytest + Ruff |

---

## 📄 Licencia

MIT
