# Déploiement Heroku - Guide Rapide

## ✅ Fichiers Prêts

Tous les fichiers nécessaires sont déjà configurés :
- ✅ `Procfile` - Commande de démarrage
- ✅ `.python-version` - Python 3.11 (recommandé par Heroku)
- ✅ `requirements.txt` - Dépendances à la racine (sans bibliothèques privées)
- ✅ `.slugignore` - Exclusion fichiers inutiles

## 🚀 Déploiement en 3 Étapes

### 1. Configurer MongoDB Atlas (Base de Données)

1. Créez un compte gratuit sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créez un cluster gratuit (M0)
3. Créez un utilisateur de base de données
4. Récupérez votre URL de connexion :
   ```
   mongodb+srv://username:password@cluster.mongodb.net/portfolio_tracker
   ```

### 2. Variables d'Environnement Heroku

Dans les paramètres de votre app Heroku, ajoutez :

```bash
# MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/portfolio_tracker
DB_NAME=portfolio_tracker

# API Keys
BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia

# CORS (Remplacez par votre URL Heroku)
CORS_ORIGINS=https://votre-app.herokuapp.com,https://votre-frontend.netlify.app
```

### 3. Déployer via GitHub

1. **Connectez GitHub à Heroku** :
   - Dashboard Heroku → Votre App → Deploy
   - Deployment method → GitHub
   - Connectez votre repository

2. **Déployez** :
   - Sélectionnez la branche `main`
   - Cliquez sur "Deploy Branch"

3. **Activez les Dynos** :
   - Resources → web → ON

## 🎯 Frontend (Option Séparée - Recommandée)

### Option A : Netlify/Vercel (Gratuit)

1. Déployez le dossier `frontend/` sur Netlify ou Vercel
2. Ajoutez la variable d'environnement :
   ```
   REACT_APP_BACKEND_URL=https://votre-app.herokuapp.com
   ```

### Option B : Servir depuis Heroku

Modifiez le `Procfile` :
```
release: cd frontend && npm install && npm run build
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
```

Ajoutez dans `backend/server.py` (après `app = FastAPI()`) :
```python
from fastapi.staticfiles import StaticFiles
import os

if os.path.exists("../frontend/build"):
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
```

## 🔧 Commandes Utiles

```bash
# Voir les logs en temps réel
heroku logs --tail --app votre-app

# Redémarrer l'application
heroku restart --app votre-app

# Vérifier les variables
heroku config --app votre-app

# Ouvrir l'app
heroku open --app votre-app
```

## ⚠️ Notes Importantes

### API Binance
- Peut être bloquée dans certaines régions
- Le code gère déjà les erreurs (affiche "..." si indisponible)
- Alternative : Remplacez par CoinGecko dans `server.py`

### MongoDB
- N'utilisez JAMAIS l'URL locale en production
- Utilisez toujours MongoDB Atlas pour Heroku
- Whitelist IP: 0.0.0.0/0 (toutes les IPs) dans Atlas

### CORS
- Mettez à jour `CORS_ORIGINS` avec vos vraies URLs
- Incluez à la fois backend ET frontend
- Format : `https://domain1.com,https://domain2.com`

## 🐛 Dépannage

### Build Failed - Requirements.txt
```bash
# Vérifiez que requirements.txt est à la RACINE et ne contient pas emergentintegrations
ls -la /app/requirements.txt
grep -v "emergentintegrations" requirements.txt
```

### Python Version Warning
- Heroku recommande maintenant `.python-version` au lieu de `runtime.txt`
- ✅ Déjà configuré avec `.python-version` contenant `3.11`

### Application Error
```bash
# Vérifiez les logs
heroku logs --tail --app votre-app

# Vérifiez MongoDB connection
# Erreur courante : IP non whitelistée dans Atlas
```

### Frontend ne charge pas
```bash
# Vérifiez REACT_APP_BACKEND_URL
# DOIT pointer vers l'URL Heroku du backend
```

## 📚 Ressources

- [Heroku Python](https://devcenter.heroku.com/articles/getting-started-with-python)
- [MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Besoin d'aide ?** Consultez `DEPLOYMENT_HEROKU.md` pour le guide complet.
