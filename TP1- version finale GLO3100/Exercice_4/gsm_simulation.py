#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation complète du protocole Mini-GSM
"""

from sim_card import SIMCard
from network_operator import NetworkOperator
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets


class GSMSimulation:
    def __init__(self):
        self.sim = None
        self.operator = None
        self.session_key = None
        self.aes_gcm = None

    def setup(self):
        """Initialise la simulation"""
        try:
            self.sim = SIMCard()
            self.operator = NetworkOperator()
            print("Simulation initialisee")
            return True
        except Exception as e:
            print(f"[X] Erreur d'initialisation: {e}")
            return False

    def authenticate(self) -> bool:
        """Exécute le protocole d'authentification"""
        print("\n=== AUTHENTIFICATION GSM ===")

        # 1. Alice envoie son IMSI
        imsi = self.sim.get_imsi()
        print(f"[+] Alice envoie IMSI: {imsi}")

        # 2. Bob génère et envoie un challenge
        challenge, verify_callback = self.operator.authenticate_subscriber(imsi)
        if challenge is None:
            return False

        # 3. La SIM calcule la réponse
        response = self.sim.compute_response(challenge)
        print(f"[<-] Alice repond: {response.hex()}")

        # 4. Bob vérifie et établit la session
        if verify_callback(response):
            # 5. Dérivation des clés de session
            self.session_key = self.sim.derive_session_key(challenge)
            operator_key = self.operator.get_session_key(imsi)

            # Vérification que les clés sont identiques
            if self.session_key == operator_key:
                self.aes_gcm = AESGCM(self.session_key)
                print("[OK] Session securisee etablie")
                return True
            else:
                print("[X] Cles de session differentes!")
                return False

        return False

    def send_encrypted_message(self, message: str) -> tuple:
        """Chiffre et envoie un message"""
        if not self.aes_gcm:
            raise Exception("Session non etablie")

        nonce = secrets.token_bytes(12)
        plaintext = message.encode("utf-8")
        ciphertext = self.aes_gcm.encrypt(nonce, plaintext, None)

        return nonce, ciphertext

    def receive_encrypted_message(self, nonce: bytes, ciphertext: bytes) -> str:
        """Déchiffre un message reçu"""
        if not self.aes_gcm:
            raise Exception("Session non etablie")

        plaintext = self.aes_gcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def secure_messaging_demo(self):
        """Démontre la messagerie sécurisée"""
        print("\n=== MESSAGERIE SECURISEE ===")

        messages = [
            "Hello, this is a secure message!",
            "La cryptographie, c'est fantastique!",
            "[SECRET] Message ultra-secret"
        ]

        for msg in messages:
            print(f"\n[->] Message original: {msg}")

            # Chiffrement
            nonce, ciphertext = self.send_encrypted_message(msg)
            print(f"[#] Message chiffre: {ciphertext.hex()}")
            print(f"[#] Nonce: {nonce.hex()}")

            # Déchiffrement
            decrypted = self.receive_encrypted_message(nonce, ciphertext)
            print(f"[<-] Message dechiffre: {decrypted}")

            # Vérification
            if msg == decrypted:
                print("[OK] Chiffrement/dechiffrement OK")
            else:
                print("[X] Erreur de chiffrement/dechiffrement")


def main():
    sim = GSMSimulation()

    if not sim.setup():
        print("[X] Impossible de demarrer la simulation")
        print("[!] Assurez-vous d'avoir lance sim_manufacturer.py d'abord")
        return

    if sim.authenticate():
        sim.secure_messaging_demo()
    else:
        print("[X] Authentification echouee")


if __name__ == "__main__":
    main()