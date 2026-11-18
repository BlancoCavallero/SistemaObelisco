"""Fail if a tracked file is too large for the repository.

GitHub rejects files over 100 MB, and a 100 MB reference PDF in history makes every clone
slow forever. This guard runs in CI so the problem is caught at the pull request instead of
at the push.
"""

import os
import subprocess
import sys

LIMITE_MB = 5
LIMITE_BYTES = LIMITE_MB * 1024 * 1024


def grandes(entradas, limite_mb=LIMITE_MB):
    """Return (path, size) pairs above the limit. Pure: easy to test."""
    limite = limite_mb * 1024 * 1024
    return [(ruta, tamano) for ruta, tamano in entradas if tamano > limite]


def archivos_versionados(raiz="."):
    salida = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, text=True, cwd=raiz, check=True
    ).stdout
    for ruta in salida.split("\0"):
        if not ruta:
            continue
        try:
            yield ruta, os.path.getsize(os.path.join(raiz, ruta))
        except OSError:
            continue


def main():
    grandes_encontrados = grandes(list(archivos_versionados()))
    if not grandes_encontrados:
        print(f"Sin archivos versionados de mas de {LIMITE_MB} MB.")
        return 0

    print(f"Archivos versionados de mas de {LIMITE_MB} MB:", file=sys.stderr)
    for ruta, tamano in grandes_encontrados:
        print(f"  {tamano / 1048576:8.1f} MB  {ruta}", file=sys.stderr)
    print(
        "\nUn archivo asi no va al repositorio: usa almacenamiento externo o "
        "agregalo al .gitignore.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
