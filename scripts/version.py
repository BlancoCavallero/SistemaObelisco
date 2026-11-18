"""Semantic version calculation from conventional commits.

Deliberately a small, readable script instead of a third-party release action: this
repository has one maintainer, and a rule that cannot be read and debugged in two years
is a rule that will be bypassed.

Usage:
    python -m scripts.version --tags "v0.1.0 v0.2.0" --commits-file commits.txt
    python -m scripts.version --last-tag v0.1.0 --message "feat: agrega ventas"
"""

import argparse
import re
import sys

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def ultima_version(tags):
    """Return the highest vX.Y.Z tag as X.Y.Z, or None. Ignores anything else."""
    mejores = []
    for tag in tags:
        match = SEMVER_RE.match(tag.strip())
        if match:
            mejores.append(tuple(int(parte) for parte in match.groups()))
    if not mejores:
        return None
    return ".".join(str(parte) for parte in max(mejores))


def _clasificar(mensajes):
    """Return 'major', 'minor' or 'patch' for the strongest change found."""
    nivel = "patch"
    for mensaje in mensajes:
        primera = mensaje.strip().splitlines()[0] if mensaje.strip() else ""
        cuerpo = mensaje

        rompe = "BREAKING CHANGE:" in cuerpo or bool(
            re.match(r"^\w+(\([^)]*\))?!:", primera)
        )
        if rompe:
            return "major"

        if re.match(r"^feat(\([^)]*\))?:", primera):
            nivel = "minor"

    return nivel


def next_version(actual, mensajes):
    """Compute the next version. Before 1.0.0 a breaking change bumps minor, not major."""
    if actual is None:
        return "0.1.0"

    mayor, menor, parche = (int(parte) for parte in actual.split("."))
    nivel = _clasificar(mensajes)

    if nivel == "major" and mayor == 0:
        nivel = "minor"

    if nivel == "major":
        return f"{mayor + 1}.0.0"
    if nivel == "minor":
        return f"{mayor}.{menor + 1}.0"
    return f"{mayor}.{menor}.{parche + 1}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate the next semver from commits.")
    parser.add_argument("--tags", default="", help="All known tags, space or newline separated.")
    parser.add_argument("--last-tag", default="", help="Latest release tag, if any.")
    parser.add_argument("--commits-file", help="File with one commit message per blank line.")
    parser.add_argument("--message", action="append", default=[], help="A commit message.")
    args = parser.parse_args(argv)

    if args.last_tag:
        actual = ultima_version([args.last_tag])
    elif args.tags:
        actual = ultima_version(args.tags.split())
    else:
        actual = None

    mensajes = list(args.message)
    if args.commits_file:
        with open(args.commits_file, encoding="utf-8") as archivo:
            bloque = []
            for linea in archivo.read().splitlines():
                if linea.strip():
                    bloque.append(linea)
                elif bloque:
                    mensajes.append("\n".join(bloque))
                    bloque = []
            if bloque:
                mensajes.append("\n".join(bloque))

    print(next_version(actual, mensajes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
