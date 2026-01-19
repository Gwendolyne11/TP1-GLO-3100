#!/usr/bin/env python3
"""
Fabricant de SIM - Génère les IMSI et clés secrètes
"""

import json
import csv
import os
import secrets
from pathlib import Path

class SIMManufacturer:
    def __init__(self, sim_file: str = "sim.json", db_file: str = "operator_db.csv"):
        self.mcc = "302"  # Canada
        self.mnc = "610"  # Bell (exemple)
        self.sim_file = sim_file
        self.db_file = db_file
        
    def generate_imsi(self) -> str:
        """Génère un IMSI aléatoire au format canadien"""
        # TODO: Générer un MSIN de 9 chiffres aléatoirement
        # https://docs.python.org/3/library/secrets.html#secrets.randbelow
        # msin =  ...
        msin = "".join(str(os.urandom(1)[0] % 10) for _ in range(9))
        return self.mcc + self.mnc + msin
    
    def generate_secret_key(self,length: int = 16) -> bytes:
        """Génère une clé secrète de 128 bits (16 bytes)"""
        # TODO: Générer 16 bytes aléatoirement avec secrets
        # https://docs.python.org/3/library/secrets.html#secrets.token_bytes
        return secrets.token_bytes(length)
    def create_sim_card(self, imsi: str = None) -> dict:
        """Crée une carte SIM avec IMSI et clé secrète"""
        if imsi is None:
            imsi = self.generate_imsi()
        
        secret_key = self.generate_secret_key()
        
        sim_data = {
            "imsi": imsi,
            "k": secret_key.hex()
        }
        return sim_data
    
    def save_sim_to_file(self, sim_data: dict, filename: str = "sim.json"):
        """Sauvegarde la SIM dans un fichier JSON"""
        # TODO: Sauvegarder sim_data dans le fichier JSON
        # https://docs.python.org/3/library/json.html#json.dump
        Path(self.sim_file).write_text(json.dumps(sim_data, indent=2), encoding="utf-8")

    
    def register_to_operator(self, sim_data: dict, db_file: str = "operator_db.csv"):
        """
                Enregistre l'abonné dans la base opérateur (CSV: imsi,k).
                Crée le fichier s'il n'existe pas.
                """
        file_exists = Path(self.db_file).exists()
        with open(self.db_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["imsi", "k"])
            writer.writerow([sim_data["imsi"], sim_data["k"]])


        
        # TODO: Ajouter une ligne dans le CSV avec l'IMSI et la clé
        # Format: imsi,k_hex
        # https://docs.python.org/3/library/csv.html#csv.writer


def main():
    manufacturer = SIMManufacturer()
    
    print("=== Fabricant de SIM ===")
    print("Génération d'une nouvelle carte SIM...")
    
    # Créer une SIM
    sim = manufacturer.create_sim_card()
    print(f"IMSI généré: {sim['imsi']}")
    print(f"Clé secrète: {sim['k']}")
    
    # Sauvegarder
    manufacturer.save_sim_to_file(sim)
    manufacturer.register_to_operator(sim)
    
    print("Carte SIM créée et enregistrée")

if __name__ == "__main__":
    main()
