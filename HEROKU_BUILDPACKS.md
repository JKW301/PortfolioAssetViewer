# 🚀 DÉPLOYER FRONTEND + BACKEND SUR HEROKU

## ⚡ Configuration Buildpacks (OBLIGATOIRE)

Heroku doit savoir qu'il faut Node.js ET Python. Exécute ces commandes :

```bash
# 1. Supprimer les anciens buildpacks
heroku buildpacks:clear --app patrimoine-090973d2f6ba

# 2. Ajouter Node.js (pour le frontend)
heroku buildpacks:add heroku/nodejs --app patrimoine-090973d2f6ba

# 3. Ajouter Python (pour le backend)
heroku buildpacks:add heroku/python --app patrimoine-090973d2f6ba

# 4. Vérifier
heroku buildpacks --app patrimoine-090973d2f6ba
```

**Tu dois voir** :
```
=== patrimoine-090973d2f6ba Buildpack URLs
1. heroku/nodejs
2. heroku/python
```

## 📋 Vérifier les Fichiers

Ces fichiers DOIVENT exister :

```
/app/
├── package.json          ← Build frontend (heroku-postbuild)
├── requirements.txt      ← Dépendances Python
├── Procfile             ← Commande de démarrage
├── .python-version      ← Version Python
└── frontend/
    ├── package.json     ← Dependencies React
    └── src/             ← Code React
```

## 🔄 Déployer

```bash
git add .
git commit -m "Configure buildpacks frontend + backend"
git push heroku main
```

## 📊 Logs de Build (Ce Que Tu Dois Voir)

```
-----> Building on the Heroku-24 stack
-----> Using buildpack: heroku/nodejs
-----> Node.js app detected
       Installing node modules
       Running heroku-postbuild script
       > cd frontend && npm install && npm run build
       Creating optimized production build...
       ✅ Frontend built successfully

-----> Using buildpack: heroku/python
-----> Python app detected
       Installing requirements.txt
       ✅ Python dependencies installed

-----> Discovering process types
       Procfile declares types -> web

-----> Launching...
       ✅ Released v15
       https://patrimoine-090973d2f6ba.herokuapp.com/ deployed to Heroku
```

## ✅ Vérification Finale

```bash
# Voir les logs
heroku logs --tail --app patrimoine-090973d2f6ba

# Doit afficher :
✅ Frontend build found at: /app/frontend/build
✅ Database tables created successfully
✅ Application startup complete
```

## 🎯 Résultat

**URL** : https://patrimoine-090973d2f6ba.herokuapp.com

**Tu auras** :
- ✅ Frontend React (page de login, dashboard, graphiques)
- ✅ Backend FastAPI (API + sert le frontend)
- ✅ Base de données MySQL
- ✅ **TOUT SUR HEROKU**

---

## 🆘 Si Ça Ne Marche Pas

### Problème : "Could not detect buildpack"
```bash
heroku buildpacks:set heroku/nodejs --app patrimoine-090973d2f6ba
heroku buildpacks:add heroku/python --app patrimoine-090973d2f6ba
```

### Problème : "npm not found"
```bash
# Vérifier que Node.js est en premier
heroku buildpacks --app patrimoine-090973d2f6ba
# Si Python est en premier, inverser :
heroku buildpacks:clear --app patrimoine-090973d2f6ba
heroku buildpacks:add heroku/nodejs --app patrimoine-090973d2f6ba
heroku buildpacks:add heroku/python --app patrimoine-090973d2f6ba
```

### Problème : "Frontend not found"
```bash
# Vérifier que le build s'est créé
heroku run ls -la /app/frontend/build/ --app patrimoine-090973d2f6ba
```

---

**COMMENCE PAR CONFIGURER LES BUILDPACKS CI-DESSUS !**
