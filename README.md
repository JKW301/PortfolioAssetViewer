# Portfolio Tracker

Un site web de suivi d'investissements pour suivre l'évolution de vos actions, cryptomonnaies et pièces de monnaie.

## Fonctionnalités

- **Suivi multi-actifs** : Cryptomonnaies, Actions, Pièces de monnaie
- **Prix en temps réel** :
  - Cryptomonnaies via Binance API
  - Actions via Yahoo Finance
  - Pièces via web scraping personnalisé (URL + sélecteur CSS)
- **Conversion automatique en euros**
- **Historique** : Sauvegardez des instantanés et visualisez l'évolution de votre portfolio
- **Dashboard professionnel** : Interface sobre et élégante avec thème sombre

## Technologies

### Backend
- FastAPI (Python)
- MongoDB (base de données)
- Binance API (crypto)
- yfinance (actions)
- BeautifulSoup (scraping)

### Frontend
- React
- TailwindCSS
- Recharts (graphiques)
- Shadcn/UI (composants)

## Installation Locale

### Prérequis
- Python 3.11
- Node.js 16+
- MongoDB

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

## Déploiement

Consultez [RENDER_DEPLOY.md](./RENDER_DEPLOY.md) pour les instructions de déploiement sur Render.

## Configuration

### Variables d'environnement Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio_tracker
CORS_ORIGINS=*
BINANCE_API_KEY=votre_clé_api
```

### Variables d'environnement Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Utilisation

1. **Ajouter des investissements** : Cliquez sur "Ajouter" dans chaque section
2. **Voir les prix actuels** : Les prix sont récupérés automatiquement
3. **Créer un instantané** : Cliquez sur "Sauvegarder" pour enregistrer l'état actuel
4. **Consulter l'historique** : Accédez à la page "Historique" pour voir l'évolution

## Notes

- L'API Binance peut être restreinte dans certaines régions
- Pour le scraping de pièces, testez vos sélecteurs CSS sur le site cible
- Les prix sont convertis automatiquement en euros via exchangerate-api.com

## Licence

MIT