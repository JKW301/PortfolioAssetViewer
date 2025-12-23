# Déploiement sur Heroku

Ce guide vous explique comment déployer votre application Portfolio Tracker sur Heroku.

## Prérequis

1. Compte GitHub
2. Compte Heroku (gratuit)
3. Code de l'application poussé sur GitHub

## Structure du Projet

```
/app/
├── backend/          # API FastAPI
├── frontend/         # Application React
├── Procfile         # Configuration Heroku ✅
├── runtime.txt      # Version Python ✅
├── requirements.txt # Dépendances Python (racine) ✅
└── .slugignore      # Fichiers à exclure du déploiement ✅
```

**IMPORTANT** : Le fichier `requirements.txt` DOIT être à la racine pour Heroku, pas dans `backend/`.

## Étapes de Déploiement

### 1. Fichiers Heroku (Déjà Créés)

Les fichiers suivants sont déjà configurés :

**Procfile** :
```
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1
```

**runtime.txt** :
```
python-3.11.0
```

**requirements.txt** (à la racine) :
- Copié depuis `backend/requirements.txt`
- Contient toutes les dépendances Python

**.slugignore** :
- Exclut les fichiers inutiles du build (tests, node_modules, etc.)

### 2. Configuration MongoDB

Heroku nécessite une base de données MongoDB externe :

1. Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (gratuit)
2. Créez un cluster gratuit
3. Récupérez votre URL de connexion MongoDB

### 3. Variables d'Environnement Heroku

Dans les paramètres de votre application Heroku, ajoutez ces variables :

```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
DB_NAME=portfolio_tracker
CORS_ORIGINS=*
BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
```

### 4. Déploiement via GitHub

1. Connectez votre repository GitHub à Heroku :
   - Allez sur le Dashboard Heroku
   - Créez une nouvelle app
   - Dans l'onglet "Deploy", choisissez "GitHub"
   - Connectez votre repository
   - Activez "Automatic Deploys" (optionnel)

2. Déployez manuellement :
   - Cliquez sur "Deploy Branch"

### 5. Build du Frontend

Pour servir le frontend via Heroku, deux options :

**Option A : Servir depuis le backend**
Ajoutez dans votre `backend/server.py` après `app = FastAPI()` :
```python
from fastapi.staticfiles import StaticFiles

# Servir le build React
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
```

Modifiez le `Procfile` :
```
release: cd frontend && yarn install && yarn build
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Option B : Déployer séparément sur Netlify/Vercel (Recommandé)**
- Déployez le backend sur Heroku
- Déployez le frontend sur Netlify/Vercel
- Mettez à jour `REACT_APP_BACKEND_URL` avec l'URL Heroku

### 6. Configuration CORS

Dans `backend/server.py`, mettez à jour CORS_ORIGINS avec votre domaine frontend :
```python
CORS_ORIGINS=https://votre-app.netlify.app,https://votre-app-heroku.herokuapp.com
```

## Notes Importantes

### API Binance
L'API Binance peut être bloquée dans certaines régions. Si vous rencontrez des erreurs :
- Le code gère déjà ces erreurs avec un fallback
- Les prix crypto afficheront simplement "..." si Binance n'est pas accessible
- Vous pouvez remplacer par une autre API (CoinGecko, CoinMarketCap, etc.)

### Web Scraping
Pour le scraping des pièces de monnaie :
- Testez vos sélecteurs CSS localement avant
- Certains sites peuvent bloquer le scraping
- Utilisez des délais raisonnables entre les requêtes

## Architecture Finale

```
┌─────────────────┐
│   Frontend      │ (Netlify/Vercel)
│   React App     │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│   Backend       │ (Heroku)
│   FastAPI       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB       │ (Atlas)
│   Database      │
└─────────────────┘
```

## Commandes Utiles

```bash
# Voir les logs Heroku
heroku logs --tail

# Redémarrer l'application
heroku restart

# Accéder au shell
heroku run bash

# Vérifier les variables d'environnement
heroku config
```

## Support

Pour toute question sur le déploiement Heroku, consultez :
- [Documentation Heroku Python](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Documentation MongoDB Atlas](https://docs.atlas.mongodb.com/)
