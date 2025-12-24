# 🛒 Smart Price Web Scraping

> **Monitoramento Inteligente de Preços com Dados Reais**

Este projeto é um agregador de preços que utiliza técnicas avançadas de Web Scraping para buscar dados em tempo real de grandes e-commerce (Mercado Livre, Magazine Luiza, Amazon via Bing) e apresentar as melhores ofertas para o usuário.

## 🚀 Funcionalidades Principais

*   **Busca em Tempo Real (Real-Time Scraping)**: Dados extraídos na hora, garantindo preços atualizados.
*   **Bing Shopping Integrado**: Utiliza o Bing como agregador robusto para contornar bloqueios de bots comuns em sites individuais.
*   **Heurística de Parsing**: Algoritmos inteligentes que identificam produtos visualmente (Preço + Imagem + Link), tornando o scraper resiliente a mudanças de layout (CSS).
*   **Modo Stealth (Indetectável)**: Uso de Playwright com flags especiais para simular comportamento humano e evitar bloqueios (403/Captcha).
*   **Histórico no Firebase**: Integração com Firestore para salvar termos pesquisados (opcional).
*   **Segurança**: Gerenciamento de chaves via variáveis de ambiente (`.env`) e scripts de setup seguros.

## 🛠️ Tecnologias Utilizadas

*   **Backend**: Python 3.10+, FastAPI, Uvicorn.
*   **Scraping**: Playwright (Browser Automation), BeautifulSoup4 (HTML Parsing).
*   **Frontend**: HTML5, CSS3 (Moderno/Responsivo), JavaScript (Vanilla).
*   **Banco de Dados**: Firebase Firestore (NoSQL).

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos
*   python 3.9+ 
*   pip

### 2. Configuração do Backend
```bash
# Clone o repositório
git clone https://github.com/LeoRodrigues290/Smart-Price-Web-Scraping-.git
cd Smart-Price-Web-Scraping-

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale os navegadores do Playwright
playwright install chromium
```

### 3. Configuração de Segurança (.env)
Crie um arquivo `.env` na raiz do projeto com suas credenciais:
```ini
FIREBASE_API_KEY=SuaApiKeyAqui
FIREBASE_PROJECT_ID=SeuProjectIdAqui
```
> **Nota**: Nunca comite este arquivo!

### 4. Configuração do Frontend
Para gerar o arquivo de configuração seguro do frontend:
```bash
python3 scripts/setup_config.py
```

### 5. Execução
```bash
# Inicie o servidor Backend
uvicorn backend.main:app --reload

# O Frontend roda em qualquer servidor estático ou abrindo o arquivo index.html no navegador
```

## 🔒 Arquitetura de Segurança
*   **Chaves de API**: Não são expostas no código fonte versionado.
*   **Google Credentials**: O backend busca `serviceAccountKey.json` localmente para escritas no banco; se não encontrar, roda em modo "Safe" (Leitura/Offline).
*   **Commits Limpos**: Histórico git auditado para garantir zero vazamento de segredos.

## ⚠️ Sobre Bloqueios e Performance
Scraping depende da disponibilidade dos sites alvo. 
*   Para mitigar bloqueios, usamos **Timeouts de 15s**. Se um site (ex: Magalu) demorar demais, ele é abortado para não travar a experiência do usuário, e os resultados do Bing assumem a prioridade.

---
Desenvolvido por Leo Rodrigues.
