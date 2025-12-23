# 🎉 JawsDB Maria (MySQL) - Configuration Heroku GRATUITE

## ✅ GRATUIT : JawsDB Maria

**Base de données MySQL/MariaDB gratuite et simple !**

---

## 🚀 Installation JawsDB Maria

### ✅ Vous l'avez déjà fait !

Si vous avez cliqué sur "Submit Order Form" dans Heroku, JawsDB Maria est déjà installé !

### Vérification

```bash
# Voir les add-ons installés
heroku addons --app patrimoine-090973d2f6ba

# Doit afficher :
# jawsdb-maria (kitefin-shared)  free
```

```bash
# Voir les variables
heroku config --app patrimoine-090973d2f6ba

# Doit inclure :
# DATABASE_URL: mysql://...
# JAWSDB_URL: mysql://...
```

**Note** : JawsDB crée 2 variables identiques (`DATABASE_URL` et `JAWSDB_URL`).

---

## 📋 Configuration des Autres Variables

Ajoutez CORS_ORIGINS et BINANCE_API_KEY :

```bash
heroku config:set CORS_ORIGINS=https://patrimoine-090973d2f6ba.herokuapp.com --app patrimoine-090973d2f6ba

heroku config:set BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia --app patrimoine-090973d2f6ba
```

---

## 🔄 Déployer et Redémarrer

Si vous avez fait des changements au code :

```bash
# Push vers Heroku (si connecté via Git)
git push heroku main

# Ou redémarrer l'app
heroku restart --app patrimoine-090973d2f6ba
```

---

## ✅ Vérification Complète

```bash
# 1. Voir toutes les variables
heroku config --app patrimoine-090973d2f6ba

# Doit afficher :
# BINANCE_API_KEY:  BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
# CORS_ORIGINS:     https://patrimoine-090973d2f6ba.herokuapp.com
# DATABASE_URL:     mysql://username:password@host.com:3306/dbname
# JAWSDB_URL:       mysql://username:password@host.com:3306/dbname

# 2. Voir les logs
heroku logs --tail --app patrimoine-090973d2f6ba

# Attendez de voir :
# ✅ INFO: Database tables created successfully
# ✅ INFO: Application startup complete.
# ✅ INFO: Uvicorn running on http://0.0.0.0:XXXX
```

---

## 🎯 Tester l'Application

```bash
# Ouvrir dans le navigateur
heroku open --app patrimoine-090973d2f6ba

# Tester l'API
curl https://patrimoine-090973d2f6ba.herokuapp.com/api/auth/me
# → {"detail":"Not authenticated"} = ✅ Parfait !
```

---

## 📊 JawsDB Maria - Plan Gratuit

| Feature | Kitefin Shared (Free) |
|---------|----------------------|
| **Prix** | ✅ 0€ / mois |
| **Stockage** | 5 MB |
| **Connexions** | 10 simultanées |
| **Backup** | Non inclus |
| **Uptime** | 99%+ |

**Pour votre portfolio personnel**, 5 MB est suffisant !

---

## 🗄️ Tables Créées Automatiquement

Au premier démarrage, l'app crée ces tables :

```sql
users             -- Utilisateurs Google OAuth
user_sessions     -- Sessions d'authentification
crypto_assets     -- Cryptomonnaies
stock_assets      -- Actions  
coin_assets       -- Pièces de monnaie
history_snapshots -- Historique du portfolio
```

---

## 🔧 Commandes MySQL Utiles

### Accéder à la Base de Données

```bash
# Via Heroku CLI
heroku addons:open jawsdb-maria --app patrimoine-090973d2f6ba

# Ou obtenir les credentials
heroku config:get JAWSDB_URL --app patrimoine-090973d2f6ba
```

### Avec MySQL Client

```bash
# Extraire les credentials
DATABASE_URL=$(heroku config:get JAWSDB_URL --app patrimoine-090973d2f6ba)

# Format : mysql://username:password@hostname:port/database
# Utilisez un client MySQL comme MySQL Workbench ou DBeaver
```

---

## 🆘 Dépannage

### "DATABASE_URL not found"

```bash
# Vérifier que JawsDB est installé
heroku addons --app patrimoine-090973d2f6ba

# Si pas installé, ajoutez-le via le dashboard Heroku :
# Resources → Find more add-ons → JawsDB Maria → Kitefin Shared (Free)
```

### "Table doesn't exist"

```bash
# Les tables se créent au startup
# Redémarrez l'app
heroku restart --app patrimoine-090973d2f6ba

# Vérifiez les logs
heroku logs --tail --app patrimoine-090973d2f6ba
```

### "Too many connections"

```bash
# Limite : 10 connexions simultanées
# Redémarrez l'app
heroku restart --app patrimoine-090973d2f6ba
```

### "Communications link failure"

```bash
# MySQL timeout ou host inaccessible
# Vérifiez DATABASE_URL
heroku config:get DATABASE_URL --app patrimoine-090973d2f6ba

# Redémarrez
heroku restart --app patrimoine-090973d2f6ba
```

---

## 📈 Upgrader Plus Tard (Optionnel)

Si vous dépassez 5 MB :

```bash
# Voir les plans disponibles
heroku addons:plans jawsdb-maria

# Upgrade (payant)
heroku addons:upgrade jawsdb-maria:leopard --app patrimoine-090973d2f6ba
```

---

## ✨ Résumé

**JawsDB Maria est déjà installé !** Si vous avez cliqué "Submit Order Form", c'est fait.

**Il reste juste à configurer 2 variables** :

```bash
heroku config:set CORS_ORIGINS=https://patrimoine-090973d2f6ba.herokuapp.com --app patrimoine-090973d2f6ba

heroku config:set BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia --app patrimoine-090973d2f6ba
```

**Puis vérifiez les logs** :

```bash
heroku logs --tail --app patrimoine-090973d2f6ba
```

**Votre app sera EN LIGNE !** 🚀

---

## 🎉 Prêt !

Une fois configuré, votre Portfolio Tracker sera accessible sur :
```
https://patrimoine-090973d2f6ba.herokuapp.com
```

Avec :
- ✅ Connexion Google SSO
- ✅ Suivi crypto, actions, pièces
- ✅ Graphiques d'évolution
- ✅ Base de données MySQL gratuite
