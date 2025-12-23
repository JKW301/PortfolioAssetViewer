#!/usr/bin/env python3
"""
Script de vérification des variables d'environnement pour Heroku
Lance ce script sur Heroku avec: heroku run python check_env.py
"""

import os
import sys

def check_env():
    print("=" * 60)
    print("Vérification des Variables d'Environnement")
    print("=" * 60)
    
    required_vars = {
        'MONGO_URL': 'URL de connexion MongoDB Atlas',
        'DB_NAME': 'Nom de la base de données',
    }
    
    optional_vars = {
        'BINANCE_API_KEY': 'Clé API Binance (optionnel)',
        'CORS_ORIGINS': 'Origines autorisées pour CORS',
    }
    
    all_ok = True
    
    print("\n📋 Variables REQUISES :")
    print("-" * 60)
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Masquer les valeurs sensibles
            if 'mongodb' in value.lower():
                display = value[:20] + "..." + value[-10:] if len(value) > 30 else value
            else:
                display = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display}")
            print(f"   ({description})")
        else:
            print(f"❌ {var}: NON DÉFINIE")
            print(f"   ({description})")
            all_ok = False
    
    print("\n📋 Variables OPTIONNELLES :")
    print("-" * 60)
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            display = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display}")
            print(f"   ({description})")
        else:
            print(f"⚠️  {var}: Non définie (optionnel)")
            print(f"   ({description})")
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Toutes les variables requises sont configurées !")
        print("=" * 60)
        return 0
    else:
        print("❌ Des variables requises sont manquantes.")
        print("   Configurez-les dans Heroku Settings > Config Vars")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(check_env())
