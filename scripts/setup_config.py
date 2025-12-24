import os
from dotenv import load_dotenv

def generate_frontend_config():
    load_dotenv()
    
    api_key = os.getenv("FIREBASE_API_KEY")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("❌ Erro: Variáveis FIREBASE_API_KEY e FIREBASE_PROJECT_ID não encontradas no .env")
        return

    config_content = f"""// Configuração do Firebase para o Frontend (Gerado Automaticamente)
import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import {{ getFirestore }} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

const firebaseConfig = {{
  apiKey: "{api_key}",
  authDomain: "{project_id}.firebaseapp.com",
  projectId: "{project_id}",
  storageBucket: "{project_id}.firebasestorage.app",
  messagingSenderId: "940344771172",
  appId: "1:940344771172:web:e8decd37cfdbb1e4de5571"
}};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export {{ db }};
"""
    
    with open("frontend/firebase_config.js", "w") as f:
        f.write(config_content)
    
    print("✅ Arquivo 'frontend/firebase_config.js' gerado com sucesso usando chaves do .env!")

if __name__ == "__main__":
    generate_frontend_config()
