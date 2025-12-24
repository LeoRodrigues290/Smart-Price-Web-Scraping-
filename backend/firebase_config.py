import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

db = None

def init_firebase():
    """
    Inicializa a conexão com o Firebase Admin SDK.
    Tenta ler as credenciais de variável de ambiente ou arquivo padrão.
    Se falhar, roda em modo 'offline' (sem banco).
    """
    global db
    
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not cred_path or not os.path.exists(cred_path):
        print("⚠️  AVISO: Credenciais do Firebase não encontradas.")
        print("   Rodando em modo OFFLINE (usando dados mockados).")
        return None

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase conectado com sucesso!")
        return db
    except Exception as e:
        print(f"❌ Erro ao conectar no Firebase: {e}")
        return None

def get_db():
    return db
