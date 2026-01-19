#!/usr/bin/env python3
# cacher_morceaux_dans_images.py
"""
Cache les fichiers reconstruction/partie_*.txt dans des images de image_source/
en produisant des images stéganographiées dans image_cachee/.

Usage (depuis la racine du projet) :
  python cacher_morceaux_dans_images.py --parts reconstruction --src image_source --dst image_cachee

Principes :
- Header : b"STEG|%04d|%04d|%08d|" -> permet d'identifier index/total/length
- Encodage : LSB sur canaux R,G,B (1 bit par canal) -> capacité = width*height*3 bits
- Format de sortie : PNG (éviter la compression JPEG)
"""

from pathlib import Path
from PIL import Image
import argparse
import re
import sys

MAGIC = b"STEG|"


def natural_key(p: Path):
    """Tri naturel pour 'partie_1' < 'partie_10'"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', p.name)]


def build_header(index: int, total: int, length: int) -> bytes:
    """Construit l'en-tête binaire placé avant les données."""
    return MAGIC + f"{index:04d}|{total:04d}|{length:08d}|".encode("ascii")


def bytes_to_bits(b: bytes) -> list:
    """Convertit bytes -> liste de bits (MSB first par octet)."""
    bits = []
    for byte in b:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def ensure_rgb(img: Image.Image) -> Image.Image:
    """Retourne une copie en mode RGB (ignore alpha si présent)."""
    if img.mode == "RGB":
        return img
    return img.convert("RGB")


def capacity_bits(img: Image.Image, channels: int = 3) -> int:
    """Capacité en bits (1 bit par canal utilisé)."""
    w, h = img.size
    return w * h * channels


def embed_lsb(img: Image.Image, payload: bytes, channels: int = 3) -> Image.Image:
    """
    Intègre payload (bytes) dans l'image via LSB sur canaux RGB.
    channels = 3 => R,G,B ; (not implemented: selecting which channels)
    """
    img = ensure_rgb(img)
    pixels = list(img.getdata())  # list of (R,G,B)
    flat = []
    for (r, g, b) in pixels:
        flat.extend([r, g, b])

    bits = bytes_to_bits(payload)
    needed = len(bits)
    if needed > len(flat):
        raise ValueError(f"Capacité insuffisante: besoin {needed} bits, dispo {len(flat)} bits")

    # Modifier LSBs
    for i in range(needed):
        flat[i] = (flat[i] & 0xFE) | bits[i]

    # Recomposer pixels
    it = iter(flat)
    new_pixels = []
    for _ in pixels:
        r = next(it); g = next(it); b = next(it)
        new_pixels.append((r, g, b))

    out = Image.new("RGB", img.size)
    out.putdata(new_pixels)
    return out


def parse_args():
    p = argparse.ArgumentParser(description="Cacher des parties dans des images via LSB.")
    p.add_argument("--parts", dest="parts_dir", required=True,
                   help="Dossier contenant les fichiers partie_*.txt (ex: reconstruction)")
    p.add_argument("--src", dest="src_dir", required=True,
                   help="Dossier d'images source (ex: image_source)")
    p.add_argument("--dst", dest="dst_dir", default="image_cachee",
                   help="Dossier de sortie (ex: image_cachee)")
    p.add_argument("--channels", dest="channels", type=int, default=3,
                   help="Nombre de canaux utilisés (1..3). Par défaut 3 (R,G,B).")
    return p.parse_args()


def main():
    args = parse_args()
    parts_dir = Path(args.parts_dir)
    src_dir = Path(args.src_dir)
    dst_dir = Path(args.dst_dir)
    channels = args.channels

    if channels < 1 or channels > 3:
        print("channels doit être entre 1 et 3", file=sys.stderr)
        sys.exit(2)

    if not parts_dir.is_dir():
        print(f"Le dossier des parties n'existe pas: {parts_dir}", file=sys.stderr)
        sys.exit(3)
    parts = sorted(parts_dir.glob("partie_*.txt"), key=natural_key)
    if not parts:
        print(f"Aucun fichier 'partie_*.txt' trouvé dans {parts_dir}", file=sys.stderr)
        sys.exit(4)

    images = sorted([*src_dir.glob("*.png"), *src_dir.glob("*.jpg"), *src_dir.glob("*.jpeg")])
    if len(images) < len(parts):
        print(f"Pas assez d'images source ({len(images)}) pour {len(parts)} parties", file=sys.stderr)
        sys.exit(5)

    dst_dir.mkdir(parents=True, exist_ok=True)
    total = len(parts)

    for idx, part_path in enumerate(parts, start=1):
        data = part_path.read_bytes()
        header = build_header(idx, total, len(data))
        payload = header + data

        src_img_path = images[idx - 1]
        try:
            with Image.open(src_img_path) as im:
                im_rgb = ensure_rgb(im)
                cap = capacity_bits(im_rgb, channels=channels)
                need = len(payload) * 8
                if need > cap:
                    print(f"[ERREUR] Image trop petite: {src_img_path.name} (cap {cap} bits, besoin {need} bits)", file=sys.stderr)
                    sys.exit(6)
                stego = embed_lsb(im_rgb, payload, channels=channels)
                out_name = f"stego_{idx:02d}_" + src_img_path.stem + ".png"
                stego.save(dst_dir / out_name, format="PNG")
                print(f"✓ {part_path.name} -> {out_name} (cap {cap}, besoin {need})")
        except FileNotFoundError:
            print(f"[ERREUR] Image introuvable: {src_img_path}", file=sys.stderr)
        except Exception as e:
            print(f"[ERREUR] Lors de l'encodage dans {src_img_path.name} : {e}", file=sys.stderr)
            sys.exit(7)

    print(f"\nTerminé. Images stégo dans : {dst_dir.resolve()}")


if __name__ == "__main__":
    main()
