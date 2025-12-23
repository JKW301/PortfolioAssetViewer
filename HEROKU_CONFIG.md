# Configuration pour Heroku

## Fichiers de Déploiement

### .python-version
```
3.11
```
Spécifie la version majeure de Python. Heroku installera automatiquement la dernière version patch (3.11.14).

### Procfile
```
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1
```
Commande pour démarrer l'application FastAPI.

### requirements.txt
Dépendances Python installées depuis PyPI public uniquement.
**Note** : `emergentintegrations` (bibliothèque privée) a été retirée du requirements.txt car elle n'est pas disponible sur PyPI public.

### .slugignore
Fichiers exclus du build Heroku pour réduire la taille du slug :
- node_modules
- tests
- documentation
- fichiers de design

## Variables d'Environnement Requises

Configurez ces variables dans les Settings de votre app Heroku :

```bash
# MongoDB (Requis)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=portfolio_tracker

# API Keys (Optionnel mais recommandé)
BINANCE_API_KEY=votre_clé_binance

# CORS (Important pour la sécurité)
CORS_ORIGINS=https://votre-app.herokuapp.com,https://votre-frontend.netlify.app
```

## Configuration MongoDB Atlas

1. Créez un compte gratuit sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créez un cluster M0 (gratuit)
3. Créez un utilisateur de base de données
4. **Important** : Whitelist toutes les IPs (0.0.0.0/0) dans Network Access
5. Récupérez votre URL de connexion

Format de l'URL :
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

## Commandes de Déploiement

### Via GitHub (Recommandé)
1. Poussez votre code sur GitHub
2. Connectez le repo à Heroku depuis le Dashboard
3. Activez les déploiements automatiques (optionnel)
4. Cliquez sur "Deploy Branch"

### Via Heroku CLI
```bash
# Login
heroku login

# Créer l'app
heroku create votre-app-name

# Ajouter les variables d'environnement
heroku config:set MONGO_URL="mongodb+srv://..."
heroku config:set DB_NAME="portfolio_tracker"
heroku config:set CORS_ORIGINS="https://votre-app.herokuapp.com"

# Déployer
git push heroku main

# Vérifier les logs
heroku logs --tail
```

## Frontend Séparé (Recommandé)

### Option : Netlify/Vercel
Déployez le dossier `frontend/` séparément sur Netlify ou Vercel.

**Variable d'environnement frontend** :
```
REACT_APP_BACKEND_URL=https://votre-app.herokuapp.com
```

**Avantages** :
- Frontend servi depuis CDN (plus rapide)
- Pas de build frontend sur Heroku (déploiement plus rapide)
- Meilleure séparation des préoccupations

## Authentification Google SSO

L'authentification Google fonctionne avec Emergent Auth :
- **En local** : Utilise l'infrastructure Emergent complète
- **En production** : Fonctionne automatiquement avec l'URL configurée dans `CORS_ORIGINS`

**Important** : Assurez-vous que votre URL Heroku est dans `CORS_ORIGINS`.

## Dépannage

### Build échoue avec "emergentintegrations not found"
✅ **Résolu** : Le requirements.txt a été nettoyé et ne contient plus cette dépendance privée.

### Application Error au démarrage
```bash
# Vérifiez les logs
heroku logs --tail

# Causes communes :
# 1. MONGO_URL invalide ou MongoDB Atlas pas accessible
# 2. Variables d'environnement manquantes
# 3. Port non configuré (Heroku utilise $PORT automatiquement)
```

### CORS Errors depuis le frontend
Vérifiez que `CORS_ORIGINS` contient l'URL exacte de votre frontend :
```bash
heroku config:get CORS_ORIGINS
```

### MongoDB Connection Failed
1. Vérifiez que l'IP 0.0.0.0/0 est whitelistée dans MongoDB Atlas
2. Vérifiez le format de MONGO_URL (doit inclure username, password, cluster)
3. Testez la connexion avec mongosh localement

## Monitoring

```bash
# Voir les logs en temps réel
heroku logs --tail

# Vérifier le statut
heroku ps

# Redémarrer l'app
heroku restart

# Accéder au shell
heroku run bash
```

## Optimisations

### Réduire le temps de build
Le `.slugignore` exclut déjà les fichiers inutiles.

### Workers
Le Procfile utilise `--workers 1`. Augmentez si nécessaire :
```
web: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT --workers 2
```

### Cache Python
Heroku met en cache les dépendances Python entre les builds.

## Support

- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/manually/)
