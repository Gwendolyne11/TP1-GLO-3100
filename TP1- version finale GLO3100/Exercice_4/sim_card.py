#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carte SIM - Gère l'authentification côté utilisateur
"""

import json
import hmac
import hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class SIMCard:
    def __init__(self, sim_file: str = "sim.json"):
        self.imsi = None
        self.secret_key = None
        self.load_sim_data(sim_file)

    def load_sim_data(self, sim_file: str):
        """Charge les données de la SIM depuis le fichier JSON"""
        with open(sim_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.imsi = data["imsi"]
        self.secret_key = bytes.fromhex(data["k"])

    def get_imsi(self) -> str:
        """Retourne l'IMSI de la SIM"""
        return self.imsi

    def compute_response(self, challenge: bytes) -> bytes:
        """Calcule la réponse au challenge: t = HMAC-SHA256_k(r)"""
        return hmac.new(self.secret_key, challenge, hashlib.sha256).digest()

    def derive_session_key(self, challenge: bytes, info: bytes = b"GSM-KE") -> bytes:
        """Dérive la clé de session: K_E = HKDF-SHA256(k, r, info)"""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 32 octets = 256 bits
            salt=challenge,  # sel = challenge r
            info=info,  # contexte du protocole
        )
        return hkdf.derive(self.secret_key)


def main():
    print("=== Test de la carte SIM ===")

    try:
        sim = SIMCard()
        print(f"IMSI: {sim.get_imsi()}")

        # Test avec un challenge fictif
        test_challenge = b"0123456789abcdef"
        response = sim.compute_response(test_challenge)
        session_key = sim.derive_session_key(test_challenge)

        print(f"Challenge: {test_challenge.hex()}")
        print(f"Reponse: {response.hex()}")
        print(f"Cle de session: {session_key.hex()}")

    except FileNotFoundError:
        print("Fichier SIM non trouve. Lancez d'abord sim_manufacturer.py")


if __name__ == "__main__":
    main()