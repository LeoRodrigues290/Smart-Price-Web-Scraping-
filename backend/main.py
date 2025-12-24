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

from backend.firebase_config import init_firebase, get_db

from backend.scrapers.mercadolivre import MercadoLivreScraper
from backend.scrapers.magazineluiza import MagazineLuizaScraper
import asyncio

# Inicializa Firebase
init_firebase()

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

@app.get("/api/search")
async def search_products(q: str):
    """
    Busca produtos em múltiplos sites (ML + Magalu) em paralelo.
    """
    print(f"Recebendo busca por: {q}")
    
    ml_scraper = MercadoLivreScraper()
    magalu_scraper = MagazineLuizaScraper()
    
    # Executa os dois scrapers ao mesmo tempo (Paralelismo Assíncrono)
    # Isso faz com que o tempo total seja igual ao do scraper mais lento, não a soma dos dois.
    results_ml, results_magalu = await asyncio.gather(
        ml_scraper.search(q),
        magalu_scraper.search(q)
    )
    
    # Junta tudo
    all_results = results_ml + results_magalu
    
    # Ordena pelo menor preço
    all_results.sort(key=lambda x: x['price'])
    
    return {"results": all_results}

@app.get("/api/suggestions")
async def get_suggestions(q: str = ""):
    """
    Retorna sugestões de busca.
    Prioridade: Firebase Cache -> Mock Data
    """
    if not q:
        return {"suggestions": []}
    
    suggestions = []
    db = get_db()
    
    # Tentativa 1: Buscar no Firebase (se estiver conectado)
    if db:
        try:
            # Busca produtos que começam com o termo digitado
            # Nota: Firestore não tem 'LIKE' nativo simples, usaremos str_start/str_end
            users_ref = db.collection('products')
            # Truque para simular 'startswith'
            end_q = q + '\uf8ff'
            docs = users_ref.where('title', '>=', q).where('title', '<=', end_q).limit(5).stream()
            
            suggestions = [doc.to_dict().get('title') for doc in docs]
        except Exception as e:
            print(f"Erro no Firestore: {e}")
    
    # Tentativa 2: Se não houver resultados no banco (ou banco offline), usa Mock
    if not suggestions:
        mock_db = [
            "iPhone 15 Pro Max", "iPhone 14", "Samsung Galaxy S24",
            "Notebook Dell Inspiron", "MacBook Air M2", "Sony PlayStation 5",
            "Monitor Gamer LG", "Teclado Mecânico Logitech", "Cadeira Gamer",
            "Mouse Sem Fio", "iPad Pro", "AirPods Pro"
        ]
        suggestions = [item for item in mock_db if q.lower() in item.lower()]
    
    return {"suggestions": suggestions[:5]}
