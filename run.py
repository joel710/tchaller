#!/usr/bin/env python3
"""
Script de démarrage pour Tcha-llé MVP
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Exécute une commande et affiche la sortie"""
    print(f"🔄 Exécution: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ Succès: {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {command}")
        print(f"Code de sortie: {e.returncode}")
        if e.stdout:
            print(f"Sortie: {e.stdout}")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False

def main():
    print("🚀 Démarrage de Tcha-llé MVP")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("backend").exists():
        print("❌ Erreur: Le répertoire 'backend' n'existe pas")
        sys.exit(1)
    
    # Installer les dépendances
    print("\n📦 Installation des dépendances...")
    if not run_command("pip install -r backend/requirements.txt"):
        print("❌ Échec de l'installation des dépendances")
        sys.exit(1)
    
    # Créer les tables et ajouter les données de test
    print("\n🗄️ Configuration de la base de données...")
    try:
        from backend.database import create_db_and_tables
        from backend.seed_data import create_sample_data
        
        print("Création des tables...")
        create_db_and_tables()
        print("✅ Tables créées")
        
        print("Ajout des données de test...")
        create_sample_data()
        print("✅ Données de test ajoutées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de la base de données: {e}")
        sys.exit(1)
    
    # Démarrer le serveur
    print("\n🌐 Démarrage du serveur...")
    print("Le serveur sera accessible sur: http://localhost:8000")
    print("Documentation API: http://localhost:8000/docs")
    print("Interface utilisateur: http://localhost:8000/static/index.html")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 50)
    
    try:
        # Démarrer uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage du serveur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()