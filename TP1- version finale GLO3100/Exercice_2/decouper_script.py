#!/usr/bin/env python3
"""
decouper_script.py
Découpe un script Python en N parties égales et sauvegarde les morceaux
dans un dossier de sortie reconstruction.
"""

from pathlib import Path
import math
import hashlib
import sys
import argparse


def compute_sha256_bytes(data: bytes) -> str:
    """Calcule l'empreinte SHA-256 d'un contenu binaire."""
    return hashlib.sha256(data).hexdigest()


def split_bytes_into_chunks(data: bytes, n: int):
    """Découpe les données binaires en N morceaux à peu près égaux."""
    if n <= 0:
        raise ValueError("Le nombre de parties doit être > 0.")
    if len(data) == 0:
        return [b""] * n
    chunk_size = math.ceil(len(data) / n)
    return [data[i * chunk_size:(i + 1) * chunk_size] for i in range(n)]


def decouper_script(fichier_source: str, dossier_sortie: str = "reconstruction", N: int = 4):
    """
    Découpe un script en N parties et les sauvegarde dans un dossier.

    Args:
        fichier_source: chemin du fichier à découper (ex: "script_secret.py")
        dossier_sortie: dossier où stocker les morceaux
        N: nombre de parties à créer (minimum 3)
    """
    fichier = Path(fichier_source)
    outdir = Path(dossier_sortie)
    if N < 3:
        raise ValueError("Erreur : le nombre de parties (--parts) doit être ≥ 3")
    if not fichier.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {fichier}")


    data = fichier.read_bytes()
    sha = compute_sha256_bytes(data)
    chunks = split_bytes_into_chunks(data, N)


    outdir.mkdir(parents=True, exist_ok=True)


    for i, chunk in enumerate(chunks, start=1):
        path = outdir / f"partie_{i}.txt"
        path.write_bytes(chunk)
        print(f"✓ {path.name} créé ({len(chunk)} octets)")

    # Sauvegarder le hash original
    (outdir / "sha256_original.txt").write_text(sha + "\n", encoding="utf-8")

    # Vérifier la reconstruction
    recon = b"".join(chunks)
    ok = recon == data
    print(f"\nDécoupage de '{fichier.name}' en {N} parties dans '{outdir}'")
    print(f"SHA-256 original : {sha}")
    print("Vérification reconstruction :", "OK " if ok else "ECHEC ")

    return ok


def main():

    p = argparse.ArgumentParser(description="Découper un script en N parties égales.")
    p.add_argument("--in", dest="infile", required=True, help="Fichier source à découper (ex: script_secret.py)")
    p.add_argument("--out", dest="outdir", default="reconstruction", help="Dossier de sortie (défaut: reconstruction)")
    p.add_argument("--parts", dest="parts", type=int, default=4, help="Nombre de parties (minimum 3)")
    args = p.parse_args()

    decouper_script(args.infile, args.outdir, args.parts)


if __name__ == "__main__":
    main()
