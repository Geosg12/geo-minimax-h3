
#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MANIFESTO = Path(__file__).with_name("modelos.json")


def validar_arquivo(caminho, sha256):
    if not caminho.is_file():
        return False
    hash_atual = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(8 * 1024 * 1024), b""
        ):
            hash_atual.update(bloco)
    return hash_atual.hexdigest().lower() == sha256.lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models-dir",
        default="/workspace/runpod-slim/ComfyUI/models"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFESTO
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    raiz = Path(args.models_dir).resolve()
    modelos = json.loads(
        args.manifest.read_text(encoding="utf-8")
    )

    if len(modelos) != 6:
        sys.exit("[GEO] Manifesto incompleto.")

    if not shutil.which("curl"):
        sys.exit("[GEO] curl nao encontrado.")

    for numero, modelo in enumerate(modelos, 1):
        destino = (raiz / modelo["destination"]).resolve()

        if not destino.is_relative_to(raiz):
            sys.exit("[GEO] Caminho invalido.")

        print(
            f'[GEO] {numero}/6: {modelo["name"]}',
            flush=True
        )

        if args.dry_run:
            print(modelo["url"])
            continue

        destino.parent.mkdir(parents=True, exist_ok=True)

        selo = Path(str(destino) + ".geo-ok")

        if destino.exists() and selo.exists():
            try:
                dados = json.loads(selo.read_text())
                info = destino.stat()
                esperado = {
                    "sha256": modelo["sha256"],
                    "bytes": info.st_size,
                    "mtime_ns": info.st_mtime_ns
                }
                if dados == esperado:
                    print("[GEO] Modelo ja instalado.")
                    continue
            except Exception:
                pass

        if destino.exists():
            if validar_arquivo(destino, modelo["sha256"]):
                info = destino.stat()
                selo.write_text(json.dumps({
                    "sha256": modelo["sha256"],
                    "bytes": info.st_size,
                    "mtime_ns": info.st_mtime_ns
                }))
                continue
            sys.exit(
                f"[GEO] Modelo existente invalido: {destino}"
            )

        parcial = Path(str(destino) + ".part")

        comando = [
            "curl", "-fL",
            "--retry", "12",
            "--retry-delay", "10",
            "--retry-all-errors",
            "--connect-timeout", "30",
            "-C", "-",
            "-o", str(parcial),
            modelo["url"]
        ]

        subprocess.run(comando, check=True)

        print("[GEO] Conferindo integridade...")

        if not validar_arquivo(
            parcial, modelo["sha256"]
        ):
            sys.exit(
                f"[GEO] Hash invalido: {parcial}"
            )

        os.replace(parcial, destino)
        info = destino.stat()

        selo.write_text(json.dumps({
            "sha256": modelo["sha256"],
            "bytes": info.st_size,
            "mtime_ns": info.st_mtime_ns
        }))

        print("[GEO] Modelo instalado.")

    print("[GEO] TODOS OS 6 MODELOS PRONTOS.")


if __name__ == "__main__":
    main()
