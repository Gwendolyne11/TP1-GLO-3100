#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Opérateur réseau - Gère l'authentification GSM côté réseau
"""

import csv
import secrets
import hmac
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from pathlib import Path


class NetworkOperator:
    def __init__(self, db_file: str = "operator_db.csv"):
        self.db_file = db_file
        self.subscriber_db = {}
        self.load_subscriber_database()
        self.active_sessions = {}  # imsi -> session_key

    def load_subscriber_database(self):
        """Charge la base de données des abonnés"""
        if not Path(self.db_file).exists():
            print(f"[!] Base de donnees {self.db_file} non trouvee")
            return

        count = 0
        try:
            with open(self.db_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Essayer différentes variantes de noms de colonnes
                    imsi = row.get("imsi") or row.get("IMSI")
                    k_hex = row.get("k") or row.get("K") or row.get("k_hex") or row.get("K_HEX")

                    if not imsi or not k_hex:
                        continue

                    # Nettoyer les espaces
                    imsi = imsi.strip()
                    k_hex = k_hex.strip()

                    try:
                        self.subscriber_db[imsi] = bytes.fromhex(k_hex)
                        count += 1
                    except (ValueError, AttributeError):
                        continue
        except Exception as e:
            print(f"[!] Erreur lors du chargement: {e}")

        print(f"[OK] Base chargee: {count} abonne(s).")

    def lookup_subscriber(self, imsi: str) -> bytes:
        """Recherche la clé secrète d'un abonné"""
        return self.subscriber_db.get(imsi)

    def generate_challenge(self, size: int = 16) -> bytes:
        """Génère un challenge aléatoire de 128 bits"""
        return secrets.token_bytes(size)

    def verify_response(self, imsi: str, challenge: bytes, response: bytes) -> bool:
        """Vérifie la réponse au challenge"""
        key = self.lookup_subscriber(imsi)
        if key is None:
            return False
        expected = hmac.new(key, challenge, hashlib.sha256).digest()
        return hmac.compare_digest(expected, response)

    def derive_session_key(self, imsi: str, challenge: bytes, length: int = 32,
                           info: bytes = b"GSM-KE") -> bytes:
        """Dérive la clé de session pour cet abonné"""
        key = self.lookup_subscriber(imsi)
        if key is None:
            return None
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=int(length),
            salt=challenge,
            info=info,
        )
        return hkdf.derive(key)

    def authenticate_subscriber(self, imsi: str) -> tuple:
        """
        Lance le processus d'authentification
        Retourne: (challenge, success_callback)
        """
        if imsi not in self.subscriber_db:
            print(f"[X] IMSI {imsi} non trouve dans la base")
            return None, None

        challenge = self.generate_challenge()
        print(f"[->] Challenge envoye a {imsi}: {challenge.hex()}")

        def verify_and_establish_session(response: bytes) -> bool:
            if self.verify_response(imsi, challenge, response):
                session_key = self.derive_session_key(imsi, challenge)
                self.active_sessions[imsi] = session_key
                print(f"[OK] Authentification reussie pour {imsi}")
                print(f"[+] Cle de session etablie: {session_key.hex()}")
                return True
            else:
                print(f"[X] Authentification echouee pour {imsi}")
                return False

        return challenge, verify_and_establish_session

    def get_session_key(self, imsi: str) -> bytes:
        """Récupère la clé de session active"""
        return self.active_sessions.get(imsi)


def main():
    print("=== Test de l'operateur reseau ===")

    operator = NetworkOperator()
    print(f"Abonnes enregistres: {len(operator.subscriber_db)}")

    # Lister les abonnés
    for imsi in operator.subscriber_db:
        print(f"  - {imsi}")


if __name__ == "__main__":
    main()