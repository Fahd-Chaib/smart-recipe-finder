# Smart Recipe Finder 🍽️

Application de recommandation de recettes basée sur la recherche sémantique (embeddings).

## Stack
- Streamlit (frontend)
- Flask (backend)
- MongoDB (stockage recettes)
- ChromaDB (base vectorielle)
- SentenceTransformers (embeddings)
- Gemini (optionnel pour génération de texte)

## Lancer le projet
### 1) Backend
```bash
cd backend
pip install -r requirements.txt
python app.py

###2) Frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py
