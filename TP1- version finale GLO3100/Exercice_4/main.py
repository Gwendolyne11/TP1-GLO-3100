#!/usr/bin/env python3
"""
Démonstration complète du système Mini-GSM
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable] + command, capture_output=True, text=True, timeout=30,encoding='utf-8',  # Forcer UTF-8
            errors='replace'
        )

        if result.returncode == 0:
            print("✅ Succès!")
            if result.stdout.strip():
                print("\n📋 Sortie:")
                print(result.stdout)
        else:
            print("❌ Erreur!")
            if result.stderr.strip():
                print("\n🚨 Erreur:")
                print(result.stderr)
            if result.stdout.strip():
                print("\n📋 Sortie:")
                print(result.stdout)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ Timeout - commande trop longue")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False


def check_files():
    """Vérifie que les fichiers nécessaires existent"""
    required_files = [
        "sim_manufacturer.py",
        "sim_card.py",
        "network_operator.py",
        "gsm_simulation.py",
        "test_mini_gsm.py",
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print("❌ Fichiers manquants:")
        for file in missing:
            print(f"  - {file}")
        return False

    print("✅ Tous les fichiers requis sont présents")
    return True


def run_demo():
    """Lance la démonstration complète"""
    print("DÉMONSTRATION MINI-GSM")
    print("Simulation d'un protocole d'authentification GSM simplifié")
    print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Vérification des prérequis
    if not check_files():
        print("\n💡 Assurez-vous que tous les fichiers Python sont présents")
        return False

    success_count = 0
    total_steps = 5

    # Étape 1: Génération de SIM
    if run_command(["sim_manufacturer.py"], "1. Génération d'une carte SIM"):
        success_count += 1

    # Pause pour la lisibilité
    time.sleep(1)

    # Étape 2: Test de la SIM
    if run_command(["sim_card.py"], "2. Test de la carte SIM"):
        success_count += 1

    time.sleep(1)

    # Étape 3: Test de l'opérateur
    if run_command(["network_operator.py"], "3. Test de l'opérateur réseau"):
        success_count += 1

    time.sleep(1)

    # Étape 4: Simulation complète
    if run_command(["gsm_simulation.py"], "4. Simulation du protocole GSM complet"):
        success_count += 1

    time.sleep(1)

    # Étape 5: Tests automatisés
    if run_command(["test_mini_gsm.py"], "5. Tests automatisés"):
        success_count += 1

    # Résumé final
    print(f"\n{'=' * 60}")
    print("📊 RÉSUMÉ DE LA DÉMONSTRATION")
    print("=" * 60)
    print(f"✅ Étapes réussies: {success_count}/{total_steps}")
    print(f"📈 Taux de succès: {success_count / total_steps * 100:.1f}%")

    if success_count == total_steps:
        print("\n🎉 DÉMONSTRATION COMPLÈTE RÉUSSIE!")
        print("🔐 Le système Mini-GSM fonctionne parfaitement")

        # Affichage des fichiers générés
        print("\n📁 Fichiers générés:")
        if Path("sim.json").exists():
            print("  ✅ sim.json - Carte SIM")
        if Path("operator_db.csv").exists():
            print("  ✅ operator_db.csv - Base opérateur")

    else:
        print(f"\n⚠️  {total_steps - success_count} étape(s) ont échoué")
        print("💡 Vérifiez les messages d'erreur ci-dessus")

    print(f"\n⏰ Démonstration terminée à {time.strftime('%H:%M:%S')}")
    return success_count == total_steps


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)

