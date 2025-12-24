from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    """
    Classe base abstrata para todos os scrapers.
    Define a 'interface' que todo scraper deve seguir.
    """
    
    @abstractmethod
    async def search(self, query: str) -> List[Dict]:
        """
        Método abstrato que deve ser implementado por cada scraper.
        Recebe um termo de busca e retorna uma lista de dicionários com os produtos.
        
        Formato esperado do retorno:
        [
            {
                "title": "Nome do Produto",
                "price": 100.00,
                "currency": "BRL",
                "link": "https://...",
                "image": "https://...",
                "store": "Nome da Loja"
            },
            ...
        ]
        """
        pass
