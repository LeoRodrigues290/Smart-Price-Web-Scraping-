from .firebase_config import get_db
import datetime

def save_search_results(query: str, products: list):
    """
    Salva os resultados da busca no Firestore.
    Coleção: 'searches' -> Document: ID automático
    Sub-coleção: 'results' (opcional) ou array direto.
    """
    db = get_db()
    if not db:
        print("⚠️ Firebase não configurado (Firestore indisponível).")
        return

    try:
        # Filtra produtos sem preço ou título
        valid_products = [p for p in products if p.get('price', 0) > 0]
        
        if not valid_products:
            return

        doc_data = {
            "query": query,
            "timestamp": datetime.datetime.now(),
            "count": len(valid_products),
            "top_results": valid_products[:5] # Salva apenas top 5 para economia, ou todos se preferir
        }
        
        # Adiciona na coleção 'searches'
        db.collection("searches").add(doc_data)
        print(f"💾 Resultados para '{query}' salvos no Firestore.")
        
    except Exception as e:
        print(f"❌ Erro ao salvar no Firestore: {e}")
