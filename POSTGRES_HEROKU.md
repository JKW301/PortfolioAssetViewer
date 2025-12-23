# 🎉 PostgreSQL Heroku - Configuration en 2 Minutes !

## ✅ GRATUIT : Heroku PostgreSQL

**Pas besoin de MongoDB !** PostgreSQL est intégré à Heroku et 100% gratuit.

---

## 🚀 Installation PostgreSQL (1 commande)

### Option A : Via Terminal (Recommandé)

```bash
heroku addons:create heroku-postgresql:essential-0 --app patrimoine-090973d2f6ba
```

✅ C'est tout ! PostgreSQL est automatiquement configuré.

### Option B : Via Dashboard Heroku

1. Allez sur https://dashboard.heroku.com/apps/patrimoine-090973d2f6ba/resources
2. Cliquez "Find more add-ons"
3. Cherchez "Heroku Postgres"
4. Sélectionnez "Essential 0" (GRATUIT)
5. Cliquez "Submit Order Form"

---

## 📋 Configuration des Variables

Après installation de PostgreSQL, ajoutez les autres variables :

```bash
# Via terminal
heroku config:set CORS_ORIGINS=https://patrimoine-090973d2f6ba.herokuapp.com --app patrimoine-090973d2f6ba

heroku config:set BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia --app patrimoine-090973d2f6ba
```

Ou via Dashboard :
```
Settings → Config Vars → Add :

CORS_ORIGINS = https://patrimoine-090973d2f6ba.herokuapp.com
BINANCE_API_KEY = BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia
```

**Note** : `DATABASE_URL` est créée automatiquement par Heroku !

---

## ✅ Vérification

```bash
# Voir les variables (doit inclure DATABASE_URL)
heroku config --app patrimoine-090973d2f6ba

# Résultat attendu :
# DATABASE_URL:    postgres://...
# CORS_ORIGINS:    https://...
# BINANCE_API_KEY: BtX...
```

---

## 🔄 Redémarrer l'App

```bash
heroku restart --app patrimoine-090973d2f6ba
```

---

## 🎯 Logs de Vérification

```bash
heroku logs --tail --app patrimoine-090973d2f6ba

# Doit afficher :
✅ INFO: Database tables created successfully
✅ INFO: Application startup complete.
✅ INFO: Uvicorn running on http://0.0.0.0:XXXX
```

---

## 🎉 Tester l'App

```bash
# Ouvrir dans le navigateur
heroku open --app patrimoine-090973d2f6ba

# Tester l'API
curl https://patrimoine-090973d2f6ba.herokuapp.com/api/auth/me
# → {"detail":"Not authenticated"} = ✅ Parfait !
```

---

## 📊 PostgreSQL vs MongoDB

| Feature | PostgreSQL Heroku | MongoDB Atlas |
|---------|-------------------|---------------|
| Prix | ✅ GRATUIT | ✅ GRATUIT |
| Stockage | 1 GB | 512 MB |
| Setup | 1 commande | 5 étapes |
| Intégration | Native Heroku | Service externe |
| Backup | Automatique | Manuel |

---

## 🔧 Commandes PostgreSQL Utiles

```bash
# Accéder à la base de données
heroku pg:psql --app patrimoine-090973d2f6ba

# Voir les tables
\dt

# Infos sur la DB
heroku pg:info --app patrimoine-090973d2f6ba

# Voir les connexions
heroku pg:ps --app patrimoine-090973d2f6ba
```

---

## ⚠️ Limites du Plan Gratuit

- **Lignes max** : 10,000 lignes
- **Connexions** : 20 simultanées
- **Backup** : Non inclus

Pour votre usage (portfolio personnel), c'est largement suffisant !

---

## 🆘 Dépannage

### "relation does not exist"
```bash
# Les tables ne sont pas créées
# Redémarrez l'app, les tables se créent au startup
heroku restart --app patrimoine-090973d2f6ba
```

### "DATABASE_URL not found"
```bash
# PostgreSQL pas installé
heroku addons:create heroku-postgresql:essential-0 --app patrimoine-090973d2f6ba
```

### "too many connections"
```bash
# Redémarrez
heroku restart --app patrimoine-090973d2f6ba
```

---

## ✨ Résumé

**1 commande pour tout installer** :
```bash
heroku addons:create heroku-postgresql:essential-0 --app patrimoine-090973d2f6ba
```

**2 variables à ajouter** :
```bash
heroku config:set CORS_ORIGINS=https://patrimoine-090973d2f6ba.herokuapp.com --app patrimoine-090973d2f6ba
heroku config:set BINANCE_API_KEY=BtXraKHkudYowil8u1ez4SYjg8BZFiWBflZKmc7P7zqngPJ4uqQXpV2nujCAX0ia --app patrimoine-090973d2f6ba
```

**C'est prêt !** 🚀
