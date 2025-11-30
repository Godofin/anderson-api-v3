"""
FastAPI Application - Anderson Viagem e Turismo
Handler para Vercel
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from routes import router as event_router

# ============================================
# APLICAÇÃO PRINCIPAL
# ============================================

app = FastAPI(
    title="Anderson Turismo API",
    description="API para gerenciamento de eventos e excursões",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# MIDDLEWARE
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de requisições"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"📊 {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Erro interno do servidor",
            "detail": str(exc)
        }
    )

# ============================================
# ROTAS
# ============================================

app.include_router(event_router, prefix="/api/v1", tags=["API v1"])

# ============================================
# ENDPOINTS DE STATUS
# ============================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "name": "Anderson Turismo API",
        "version": "2.0.0",
        "status": "online",
        "database": "Neon Postgres",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check (GET)"""
    return {"status": "healthy", "timestamp": time.time()}

@app.head("/health")
async def health_check_head():
    """Health check (HEAD)"""
    return Response(status_code=200)

@app.get("/api/v1/ping")
async def ping():
    """Teste de conexão com o banco"""
    try:
        from database import execute_query
        result = execute_query("SELECT 1 as ping", fetch="one")
        return {
            "database": "connected",
            "ping": result['ping'] if result else None
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "database": "disconnected",
                "error": str(e)
            }
        )