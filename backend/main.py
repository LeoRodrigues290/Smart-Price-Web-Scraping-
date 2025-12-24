from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializando a aplicação FastAPI
# Doc: https://fastapi.tiangolo.com/
app = FastAPI(title="Smart Price API", description="API para monitoramento de preços com scraping", version="1.0.0")

# Configurando CORS (Cross-Origin Resource Sharing)
# Isso é crucial para permitir que nosso frontend (que pode rodar em outra porta/domínio)
# consiga fazer requisições para este backend.
# Por enquanto, liberando geral ("*") para facilitar o dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Rota raiz para health check simples.
    """
    return {"message": "Smart Price API is online! 🚀"}

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar se a API está respondendo corretamente.
    """
    return {"status": "ok", "service": "smart-price-api"}

@app.get("/api/suggestions")
async def get_suggestions(q: str = ""):
    """
    Retorna sugestões de busca baseadas no termo digitado.
    Por enquanto, retorna dados mockados.
    """
    if not q:
        return {"suggestions": []}
    
    # Mock data simples para teste
    mock_db = [
        "iPhone 15 Pro Max",
        "iPhone 14",
        "Samsung Galaxy S24",
        "Notebook Dell Inspiron",
        "MacBook Air M2",
        "Sony PlayStation 5",
        "Monitor Gamer LG",
        "Teclado Mecânico Logitech"
    ]
    
    # Filtro case-insensitive
    filtered = [item for item in mock_db if q.lower() in item.lower()]
    
    # Limita a 5 resultados
    return {"suggestions": filtered[:5]}
