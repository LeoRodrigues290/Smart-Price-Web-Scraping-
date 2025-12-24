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
from backend.scrapers.bing_shopping import BingShoppingScraper
from backend.database import save_search_results
from typing import List
import asyncio
import time

# Inicializa Firebase
init_firebase()

# Inicializa Scrapers globalmente
ml_scraper = MercadoLivreScraper()
magalu_scraper = MagazineLuizaScraper()
bing_scraper = BingShoppingScraper()

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
    Busca produtos em múltiplos sites (Bing, ML, Magalu) em paralelo.
    Agora usa Bing Shopping como fonte principal de Dados Reais.
    """
    print(f"Recebendo busca por: {q} - Iniciando scraping...")
    start_time = time.time()

    # Dispara buscas em paralelo
    # Priorizando Bing por ser mais estável com dados reais
    results = await asyncio.gather(
        bing_scraper.search(q),
        ml_scraper.search(q),
        magalu_scraper.search(q)
    )
    # results é uma lista de listas: [[bing_items], [ml_items], [magalu_items]]
    # Flatten: Transforma lista de listas em uma única lista plana de produtos
    all_products = []
    for r in results:
        all_products.extend(r)
    
    # Lógica de Prioridade de Exibição:
    # O Bing Shopping retorna dados reais agregados.
    # Se o Bing retornar resultados, filtramos qualquer dado 'Mock' (caso algum scraper tenha falhado e retornado fallback).
    # Isso garante que o usuário final veja APENAS produtos reais.
    real_products = [p for p in all_products if "(Mock)" not in p['store']]
    
    if real_products:
        final_products = real_products
        print(f"✅ Retornando {len(final_products)} produtos REAIS (Mocks ocultados).")
    else:
        final_products = all_products
        print(f"⚠️ Apenas Mocks disponíveis. Retornando {len(final_products)} mocks.")
    
    # Ordenação por preço
    final_products.sort(key=lambda x: x['price'])
    
    # Salva no histórico (opcional firestore)
    # save_search_results(q, final_products)

    duration = time.time() - start_time
    print(f"⏱️ Busca concluída em {duration:.2f} segundos.")
    
    return final_products

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
