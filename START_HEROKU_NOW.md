# 🚀 DÉMARRAGE RAPIDE HEROKU - 5 MINUTES

## ⚡ Actions Immédiates

### 1️⃣ MongoDB Atlas (3 min)
```
🌐 https://www.mongodb.com/cloud/atlas
1. Inscrivez-vous (gratuit)
2. Créez cluster M0 (gratuit)
3. Créez user : portfoliouser + password fort
4. Network Access → Add IP → 0.0.0.0/0
5. Copiez URL : mongodb+srv://portfoliouser:PASSWORD@cluster.mongodb.net/
```

### 2️⃣ Heroku Config (2 min)
```
🌐 https://dashboard.heroku.com/apps/patrimoine-090973d2f6ba/settings

Cliquez "Reveal Config Vars"
Ajoutez :

MONGO_URL          = mongodb+srv://portfoliouser:VotreMotDePasse@cluster.mongodb.net/
DB_NAME            = portfolio_tracker
CORS_ORIGINS       = https://patrimoine-090973d2f6ba.herokuapp.com
BINANCE_API_KEY    = BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
```

### 3️⃣ Redémarrage
```bash
heroku restart --app patrimoine-090973d2f6ba
```

## ✅ Vérification
```bash
# Voir les logs
heroku logs --tail --app patrimoine-090973d2f6ba

# Doit afficher :
✅ INFO: Application startup complete.
✅ INFO: Uvicorn running on...

# Tester l'API
curl https://patrimoine-090973d2f6ba.herokuapp.com/api/auth/me
# Résultat attendu : {"detail":"Not authenticated"}
```

## 🎉 C'est Prêt !
```
Votre app : https://patrimoine-090973d2f6ba.herokuapp.com
```

---

## 📚 Guides Détaillés

Si vous avez des problèmes, consultez :

1. **HEROKU_VISUAL_GUIDE.md** - Guide pas à pas avec captures
2. **HEROKU_FIX_NOW.md** - Résolution des erreurs courantes
3. **HEROKU_CONFIG.md** - Configuration avancée

---

## 🆘 Problèmes Fréquents

### App toujours "crashed"
```bash
# Vérifiez les variables
heroku config --app patrimoine-090973d2f6ba

# Doivent apparaître : MONGO_URL, DB_NAME, CORS_ORIGINS, BINANCE_API_KEY
```

### "Authentication failed" MongoDB
```
❌ Mot de passe incorrect dans MONGO_URL
✅ Vérifiez username:password dans l'URL
```

### Variables pas sauvegardées
```
✅ Vérifiez l'orthographe : MONGO_URL (pas MONGODB_URL)
✅ Pas d'espaces avant/après les valeurs
✅ Cliquez bien "Add" après chaque variable
```

---

## 💡 Astuce Pro

Utilisez ce script pour vérifier vos variables :
```bash
heroku run python check_env.py --app patrimoine-090973d2f6ba
```

Affiche ✅ ou ❌ pour chaque variable requise.

---

**GO ! Configurez maintenant et votre app sera en ligne ! 🚀**
