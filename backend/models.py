from pydantic import BaseModel
from typing import Optional, List

# Aqui vamos definir nossos modelos de dados usando Pydantic.
# Isso garante que os dados que entram e saem da API estejam no formato certo.

# Exemplo de modelo para um Produto (vamos usar mais tarde)
class Product(BaseModel):
    title: str
    price: float
    currency: str = "BRL"
    url: str
    image_url: Optional[str] = None
    store_name: str
