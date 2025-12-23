# Configuration Heroku - Guide Visuel Pas à Pas

## 🎯 Objectif
Configurer les variables d'environnement pour faire fonctionner votre app sur Heroku.

---

## Partie 1 : MongoDB Atlas (5 minutes)

### 1.1 Créer un Compte MongoDB Atlas
```
🌐 Allez sur : https://www.mongodb.com/cloud/atlas
📝 Cliquez : "Try Free"
✍️  Inscrivez-vous avec Google ou Email
```

### 1.2 Créer un Cluster Gratuit
```
1. Après connexion, cliquez "Build a Database"
2. Sélectionnez "M0 FREE"
3. Choisissez un provider (AWS recommandé)
4. Région : Europe (Paris/Frankfurt) ou la plus proche
5. Nom du cluster : "Cluster0" (par défaut)
6. Cliquez "Create"
⏱️  Attendez 3-5 minutes...
```

### 1.3 Créer un Utilisateur Database
```
Une popup s'ouvre automatiquement :
1. Username : portfoliouser
2. Password : [Générez un mot de passe fort]
   📝 NOTEZ CE MOT DE PASSE QUELQUE PART !
3. Cliquez "Create User"
```

### 1.4 Configurer l'Accès Réseau
```
Dans la même popup :
1. Où voir "Where would you like to connect from?"
2. Cliquez "My Local Environment"
3. IP Address : 0.0.0.0/0
4. Description : "Allow from anywhere"
5. Cliquez "Add Entry"
6. Cliquez "Finish and Close"
```

### 1.5 Obtenir l'URL de Connexion
```
1. Cliquez "Connect" sur votre cluster
2. Choisissez "Drivers"
3. Driver : Python / Version : 3.11 or later
4. Copiez l'URL qui ressemble à :
   mongodb+srv://portfoliouser:<password>@cluster0.xxxxx.mongodb.net/
   
📝 REMPLACEZ <password> par votre vrai mot de passe
   Exemple final :
   mongodb+srv://portfoliouser:MonP@ss123@cluster0.abc123.mongodb.net/
```

---

## Partie 2 : Configuration Heroku (2 minutes)

### 2.1 Accéder à Votre App
```
🌐 URL : https://dashboard.heroku.com/apps/patrimoine-090973d2f6ba
🔑 Connectez-vous avec votre compte Heroku
```

### 2.2 Ouvrir les Config Vars
```
Navigation dans l'interface Heroku :

patrimoine-090973d2f6ba
├── Overview       ← Pas ici
├── Resources      ← Pas ici
├── Deploy         ← Pas ici
├── Metrics        ← Pas ici
└── Settings       ← ✅ CLIQUEZ ICI !

Dans Settings, scrollez jusqu'à "Config Vars"
Cliquez "Reveal Config Vars"
```

### 2.3 Ajouter les Variables
```
Formulaire visible : [ KEY ] [ VALUE ] [Add]

Ajoutez chaque variable une par une :

Variable 1 :
  KEY   : MONGO_URL
  VALUE : mongodb+srv://portfoliouser:VotrePassword@cluster0.xxxxx.mongodb.net/
  [Add] ← Cliquez

Variable 2 :
  KEY   : DB_NAME
  VALUE : portfolio_tracker
  [Add] ← Cliquez

Variable 3 :
  KEY   : BINANCE_API_KEY
  VALUE : BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
  [Add] ← Cliquez

Variable 4 :
  KEY   : CORS_ORIGINS
  VALUE : https://patrimoine-090973d2f6ba.herokuapp.com
  [Add] ← Cliquez
```

---

## Partie 3 : Redémarrage (1 minute)

### 3.1 Redémarrer l'App

**Option A : Via Interface Web**
```
1. Restez dans l'onglet "Settings"
2. En haut à droite, cliquez "More" (bouton avec 3 points)
3. Sélectionnez "Restart all dynos"
4. Confirmez "Restart"
```

**Option B : Via Terminal**
```bash
heroku restart --app patrimoine-090973d2f6ba
```

### 3.2 Vérifier les Logs
```bash
# Dans votre terminal
heroku logs --tail --app patrimoine-090973d2f6ba

# Vous devriez voir :
✅ INFO:     Started server process
✅ INFO:     Waiting for application startup.
✅ INFO:     Application startup complete.
✅ INFO:     Uvicorn running on http://0.0.0.0:12345
```

---

## ✅ Vérification Finale

### Test 1 : Ouvrir l'App
```bash
heroku open --app patrimoine-090973d2f6ba
```
Vous devriez voir la page de login Google !

### Test 2 : API Backend
```bash
curl https://patrimoine-090973d2f6ba.herokuapp.com/api/auth/me
# Résultat attendu : {"detail":"Not authenticated"}
```

### Test 3 : Vérifier les Variables
```bash
heroku run python check_env.py --app patrimoine-090973d2f6ba
# Doit afficher ✅ pour MONGO_URL et DB_NAME
```

---

## 🐛 Problèmes Courants

### "Authentication failed" (MongoDB)
```
❌ Problème : Mot de passe incorrect dans MONGO_URL
✅ Solution :
   1. Vérifiez le mot de passe copié
   2. Pas de caractères spéciaux non encodés
   3. Format : mongodb+srv://user:pass@cluster.mongodb.net/
```

### "Connection timeout" (MongoDB)
```
❌ Problème : IP non whitelistée dans MongoDB Atlas
✅ Solution :
   1. MongoDB Atlas → Network Access
   2. Ajoutez 0.0.0.0/0 (Allow from anywhere)
   3. Attendez 2 minutes
```

### App toujours "crashed"
```
❌ Problème : Variables non sauvegardées ou mal formatées
✅ Solution :
   1. Heroku Settings → Config Vars
   2. Vérifiez l'orthographe : MONGO_URL (pas MONGODB_URL)
   3. Vérifiez le format de chaque valeur
   4. Redémarrez : heroku restart
```

---

## 📞 Commandes Utiles

```bash
# Voir toutes les variables configurées
heroku config --app patrimoine-090973d2f6ba

# Voir les logs en temps réel
heroku logs --tail --app patrimoine-090973d2f6ba

# Accéder au shell Heroku
heroku run bash --app patrimoine-090973d2f6ba

# Vérifier l'état des dynos
heroku ps --app patrimoine-090973d2f6ba
```

---

## 🎉 Résultat Final

Une fois tout configuré, votre Portfolio Tracker sera accessible sur :

```
🌐 https://patrimoine-090973d2f6ba.herokuapp.com
```

Vous pourrez :
- ✅ Vous connecter avec Google
- ✅ Ajouter vos cryptos, actions, pièces
- ✅ Voir votre patrimoine total en euros
- ✅ Suivre l'évolution avec des graphiques

**Bonne chance ! 🚀**
