# 🚨 URGENT : Configurer les Variables d'Environnement Heroku

## Erreur Actuelle
```
KeyError: 'MONGO_URL'
```

**Cause** : Les variables d'environnement ne sont pas configurées sur Heroku.

## ✅ Solution en 5 Minutes

### Étape 1 : Créer MongoDB Atlas (Gratuit)

1. Allez sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créez un compte gratuit
3. Créez un cluster M0 (gratuit, région proche de vous)
4. Attendez 3-5 minutes que le cluster se crée

### Étape 2 : Configurer MongoDB

1. Cliquez sur **"Connect"** sur votre cluster
2. Créez un utilisateur de base de données :
   - Username : `portfoliouser`
   - Password : Générez un mot de passe fort (notez-le !)
3. Whitelist toutes les IPs :
   - **Network Access** → **Add IP Address**
   - Choisissez **"Allow access from anywhere"** (0.0.0.0/0)
4. Récupérez votre URL de connexion :
   - Cliquez **"Connect"** → **"Connect your application"**
   - Copiez l'URL qui ressemble à :
   ```
   mongodb+srv://portfoliouser:<password>@cluster0.xxxxx.mongodb.net/
   ```
   - Remplacez `<password>` par votre vrai mot de passe

### Étape 3 : Configurer Heroku (Via Dashboard Web)

1. Allez sur [Heroku Dashboard](https://dashboard.heroku.com/apps/patrimoine-090973d2f6ba)
2. Cliquez sur votre app **"patrimoine-090973d2f6ba"**
3. Allez dans l'onglet **"Settings"**
4. Cliquez sur **"Reveal Config Vars"**
5. Ajoutez ces variables une par une :

| Key | Value |
|-----|-------|
| `MONGO_URL` | `mongodb+srv://portfoliouser:VOTRE_PASSWORD@cluster0.xxxxx.mongodb.net/` |
| `DB_NAME` | `portfolio_tracker` |
| `BINANCE_API_KEY` | `BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia` |
| `CORS_ORIGINS` | `https://patrimoine-090973d2f6ba.herokuapp.com` |

### Étape 4 : Redémarrer l'App

Après avoir ajouté les variables :
1. Restez dans **Settings**
2. Scrollez vers le haut
3. Cliquez sur **"More"** (coin supérieur droit)
4. Sélectionnez **"Restart all dynos"**

Ou via terminal :
```bash
heroku restart --app patrimoine-090973d2f6ba
```

### Étape 5 : Vérifier les Logs

```bash
heroku logs --tail --app patrimoine-090973d2f6ba
```

Vous devriez voir :
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

## 🎯 Résultat Attendu

Une fois configuré, votre app sera accessible sur :
```
https://patrimoine-090973d2f6ba.herokuapp.com
```

## ⚠️ Notes Importantes

### Format MONGO_URL
✅ **Correct** :
```
mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/
```

❌ **Incorrect** (sans le slash final ou avec caractères spéciaux non encodés) :
```
mongodb+srv://user:p@ssw0rd@cluster0.xxxxx.mongodb.net
```

Si votre mot de passe contient des caractères spéciaux (@, :, /, etc.), encodez-le :
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`

### CORS_ORIGINS
Utilisez l'URL HTTPS exacte de votre app Heroku :
```
https://patrimoine-090973d2f6ba.herokuapp.com
```

## 🆘 Dépannage Rapide

### "Authentication failed" (MongoDB)
- Vérifiez username/password dans MONGO_URL
- Vérifiez que 0.0.0.0/0 est whitelisté dans MongoDB Atlas

### "App crashed" après config
```bash
# Vérifiez que toutes les variables sont présentes
heroku config --app patrimoine-090973d2f6ba

# Redémarrez
heroku restart --app patrimoine-090973d2f6ba
```

### Voir les variables configurées
```bash
heroku config --app patrimoine-090973d2f6ba
```

## 📞 Commandes Utiles

```bash
# Voir les logs en temps réel
heroku logs --tail --app patrimoine-090973d2f6ba

# Vérifier le statut
heroku ps --app patrimoine-090973d2f6ba

# Ouvrir l'app
heroku open --app patrimoine-090973d2f6ba

# Accéder au shell
heroku run bash --app patrimoine-090973d2f6ba
```

## ✨ Une Fois Configuré

Votre Portfolio Tracker sera accessible et vous pourrez :
1. Vous connecter avec Google
2. Ajouter vos actifs (crypto, actions, pièces)
3. Voir votre patrimoine total en euros
4. Suivre l'évolution avec des graphiques

**Configurez MongoDB Atlas maintenant, ça prend 5 minutes !** 🚀
