#!/usr/bin/env python3
# Simulation.py
"""
Simuler l'ordinateur de la victime en répartissant des images stéganographiées.

Usage:
  python Simulation.py --stego image_cachee --root ordinateur_victime --mode random --seed 42

Principales options:
  --stego   : dossier contenant les images stégo (défaut: image_cachee)
  --root    : dossier racine de la simulation (défaut: ordinateur_victime)
  --mode    : mode de répartition: random | roundrobin | mapping   (défaut: random)
  --mapping : chemin vers un fichier mapping (utilisé si --mode mapping). Format: "filename,target_subdir" par ligne
  --seed    : valeur entière pour random.seed (rend l'aléatoire déterministe)
  --dry     : si présent, n'effectue que l'affichage (aucune copie)
"""

from pathlib import Path
import argparse
import shutil
import random
import sys

def ensure_dirs(root: Path):
    """Crée l'arborescence attendue pour la simulation."""
    docs = root / "Documents"
    vac = root / "Images" / "vacances"
    fam = root / "Images" / "famille"
    dl = root / "Téléchargements"
    for d in (docs, vac, fam, dl):
        d.mkdir(parents=True, exist_ok=True)

    try:
        (docs / "resume.docx").write_text("CV - (fichier simulé)\n", encoding="utf-8")
        (docs / "notes.txt").write_text("Notes de doc - (fichier simulé)\n", encoding="utf-8")
        (dl / "software.exe").write_text("", encoding="utf-8")
        (dl / "wallpaper.png").write_text("", encoding="utf-8")
    except Exception:

        pass
    return {"vacances": vac, "famille": fam, "Téléchargements": dl, "Documents": docs}

def list_stego_images(stego_dir: Path):
    """Retourne la liste des fichiers stego (png/jpg/jpeg) dans stego_dir."""
    if not stego_dir.exists():
        return []
    images = sorted([*stego_dir.glob("*.png"), *stego_dir.glob("*.jpg"), *stego_dir.glob("*.jpeg")])
    return images

def load_mapping_file(path: Path):
    """
    Lit un fichier mapping texte.
    Chaque ligne: filename,relative_target_dir
    Exemple:
      stego_01_img.png,Images/vacances
    """
    mapping = {}
    if not path.is_file():
        raise FileNotFoundError(f"Mapping file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",", 1)]
        if len(parts) != 2:
            continue
        fname, target = parts
        mapping[fname] = target
    return mapping

def simulate_copy(images, dests_map, mode="random", mapping_file=None, seed=None, dry=False):
    """
    Copie les images vers les destinations.
    images: list[Path]
    dests_map: dict with keys like 'vacances','famille','Téléchargements' -> Path
    mode: random | roundrobin | mapping
    mapping_file: dict from filename->relative target if mode == mapping
    """
    dest_keys = ["vacances", "famille", "Téléchargements"]
    if mode == "random":
        if seed is not None:
            random.seed(seed)
        for img in images:
            target_key = random.choice(dest_keys)
            dest = dests_map[target_key]
            dst_path = dest / img.name
            if dry:
                print(f"[DRY] Copier {img.name} -> {dest}")
            else:
                shutil.copy2(img, dst_path)
                print(f"Copié {img.name} -> {dest}")
    elif mode == "roundrobin":
        for i, img in enumerate(images):
            target_key = dest_keys[i % len(dest_keys)]
            dest = dests_map[target_key]
            dst_path = dest / img.name
            if dry:
                print(f"[DRY] Copier {img.name} -> {dest}")
            else:
                shutil.copy2(img, dst_path)
                print(f"Copié {img.name} -> {dest}")
    elif mode == "mapping":
        if mapping_file is None:
            raise ValueError("Mode 'mapping' nécessite un mapping_file (dict).")
        for img in images:
            target_rel = mapping_file.get(img.name)
            if not target_rel:
                print(f"Avertissement: aucune cible mapping pour {img.name} -> saut", file=sys.stderr)
                continue

            if target_rel in dests_map:
                dest = dests_map[target_rel]
            else:

                dest = Path(target_rel)
            dst_path = dest / img.name
            if dry:
                print(f"[DRY] Copier {img.name} -> {dest}")
            else:
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, dst_path)
                print(f"Copié {img.name} -> {dest}")
    else:
        raise ValueError(f"Mode inconnu: {mode}")

def parse_args():
    p = argparse.ArgumentParser(description="Simuler un ordinateur victime et y copier des images stégo.")
    p.add_argument("--stego", dest="stego_dir", default="image_cachee", help="Dossier contenant les images stégo (défaut: image_cachee)")
    p.add_argument("--root", dest="root", default="ordinateur_victime", help="Dossier racine de la simulation (défaut: ordinateur_victime)")
    p.add_argument("--mode", dest="mode", choices=["random","roundrobin","mapping"], default="random", help="Mode de répartition")
    p.add_argument("--mapping", dest="mapping", default=None, help="Fichier mapping (si --mode mapping). Format: filename,target_subdir")
    p.add_argument("--seed", dest="seed", type=int, default=None, help="Seed pour random (rend reproductible)")
    p.add_argument("--dry", dest="dry", action="store_true", help="Dry run: n'effectue pas les copies, affiche seulement")
    return p.parse_args()

def main():
    args = parse_args()
    stego_dir = Path(args.stego_dir)
    root = Path(args.root)
    mode = args.mode
    mapping_path = Path(args.mapping) if args.mapping else None
    seed = args.seed
    dry = args.dry

    # Crée la structure
    dests = ensure_dirs(root)
    images = list_stego_images(stego_dir)
    if not images:
        print(f"Aucune image stégo trouvée dans: {stego_dir}", file=sys.stderr)
        sys.exit(1)

    # Charger mapping si nécessaire
    mapping_dict = None
    if mode == "mapping":
        if mapping_path is None:
            print("Erreur: mode 'mapping' sélectionné mais aucun --mapping fourni.", file=sys.stderr)
            sys.exit(2)
        try:
            mapping_dict = load_mapping_file(mapping_path)
        except Exception as e:
            print(f"Erreur lecture mapping: {e}", file=sys.stderr)
            sys.exit(3)

    # Effectuer la simulation / copies
    print(f"Simulation: copier {len(images)} images depuis {stego_dir} vers {root} (mode={mode})")
    if dry:
        print("Dry-run activé : aucune écriture sur disque ne sera effectuée.")
    try:
        simulate_copy(images, dests, mode=mode, mapping_file=mapping_dict, seed=seed, dry=dry)
    except Exception as e:
        print(f"Erreur lors de la simulation: {e}", file=sys.stderr)
        sys.exit(4)

    print(f"\nSimulation terminée. Dossier racine : {root.resolve()}")

if __name__ == "__main__":
    main()
