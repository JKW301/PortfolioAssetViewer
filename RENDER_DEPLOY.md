# 🚀 DÉPLOYER SUR RENDER (Frontend + Backend Ensemble)

## ✅ Pourquoi Render ?

- ✅ **Supporte Node.js + Python** nativement
- ✅ **Build automatique** du frontend
- ✅ **Base de données gratuite** PostgreSQL/MySQL
- ✅ **Plus simple** que Heroku
- ✅ **Vraiment gratuit** (750h/mois)

---

## 📋 Étape 1 : Créer un Compte Render

1. Va sur [render.com](https://render.com)
2. **Sign Up** avec GitHub
3. **Autorise Render** à accéder à ton repo

---

## 🗄️ Étape 2 : Créer la Base de Données

### Via Dashboard Render

1. Clique sur **"New +"** → **"PostgreSQL"**
2. Nom : `portfolio-db`
3. Database : `portfolio_tracker`
4. Plan : **Free**
5. Clique **"Create Database"**

### Récupère l'URL

Une fois créée, copie la **"Internal Database URL"** :
```
postgres://user:password@dpg-xxxxx.oregon-postgres.render.com/portfolio_tracker
```

---

## 🌐 Étape 3 : Créer le Web Service

### Via Dashboard

1. Clique **"New +"** → **"Web Service"**
2. Connecte ton **repo GitHub**
3. Configuration :

```
Name:           portfolio-tracker
Environment:    Python 3
Region:         Oregon (ou le plus proche)
Branch:         main
Build Command:  ./build.sh
Start Command:  cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
Plan:           Free
```

### Variables d'Environnement

Ajoute ces variables dans **"Environment"** :

```
DATABASE_URL = [Colle l'URL de ta base de données]
CORS_ORIGINS = https://portfolio-tracker.onrender.com
BINANCE_API_KEY = BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
```

**⚠️ Important** : Utilise l'**Internal Database URL** de Render, pas l'External.

---

## 🔄 Étape 4 : Déployer

1. Clique **"Create Web Service"**
2. Render va :
   - Clone ton repo
   - Install Python dependencies
   - **Build le frontend React**
   - Start le backend
   - **Servir le frontend depuis le backend**

### Logs de Build (Ce Que Tu Verras)

```
==> Building...
📦 Installing Python dependencies...
🎨 Building React frontend...
   Creating an optimized production build...
   Compiled successfully!
✅ Build complete!

==> Starting service...
✅ Frontend build found at: /app/frontend/build
✅ Database tables created successfully
✅ Application startup complete
🚀 Service live at https://portfolio-tracker.onrender.com
```

---

## ✅ Vérification

### Test API
```bash
curl https://portfolio-tracker.onrender.com/api/auth/me
# → {"detail":"Not authenticated"} ✅
```

### Ouvre dans le Navigateur
```
https://portfolio-tracker.onrender.com
```

**Tu devrais voir** : Page de login Google !

---

## 📊 Architecture Finale

```
Render Web Service (Free)
├── Frontend React (/)
│   ├── Login Google
│   ├── Dashboard
│   └── Graphiques
├── Backend FastAPI (/api/*)
│   ├── Auth endpoints
│   ├── Portfolio endpoints
│   └── Sert le frontend
└── PostgreSQL Database (Free)
    └── Tables créées automatiquement
```

---

## 🎯 Avantages vs Heroku

| Feature | Render | Heroku |
|---------|--------|--------|
| Build Frontend + Backend | ✅ Natif | ❌ Compliqué |
| Base de données gratuite | ✅ PostgreSQL | ❌ Add-on tiers |
| Heures gratuites | ✅ 750h/mois | ❌ 550h/mois |
| Setup | ✅ Simple | ❌ Buildpacks |
| Auto-deploy | ✅ Oui | ✅ Oui |

---

## 🔧 Configuration Automatique

Le fichier **`render.yaml`** est déjà configuré. Render le détectera automatiquement !

Tu peux aussi déployer avec ce fichier :
1. Dans Render, **"New +"** → **"Blueprint"**
2. Connecte ton repo
3. Render lit `render.yaml` et configure tout automatiquement

---

## 🆘 Dépannage

### Build échoue - "npm not found"
✅ Normal ! Le `build.sh` install npm automatiquement.

### "Frontend not found"
Vérifie dans les logs :
```
✅ Frontend build found at: /app/frontend/build
```

Si absent, le build a échoué. Regarde les logs de build.

### Database connection error
✅ Utilise l'**Internal Database URL** (pas External)
✅ Format : `postgres://user:pass@host.render.com/db`

### CORS errors
Ajoute ton URL Render dans `CORS_ORIGINS` :
```
CORS_ORIGINS=https://ton-app.onrender.com
```

---

## 🎉 C'est Tout !

**Render build automatiquement le frontend ET backend.**

**Ton site complet sera sur une seule URL** :
```
https://portfolio-tracker.onrender.com
```

**Plus simple que Heroku. Ça marche vraiment.**

---

## 📝 Checklist Déploiement

- [ ] Compte Render créé
- [ ] Repo GitHub connecté
- [ ] Base de données PostgreSQL créée
- [ ] DATABASE_URL copiée
- [ ] Web Service créé
- [ ] Variables d'environnement configurées
- [ ] Déploiement lancé
- [ ] Logs vérifiés (build + start)
- [ ] Site testé dans le navigateur

**Bonne chance ! 🚀**
