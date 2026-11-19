"""Synchronise le dossier commun des agents IA (.agents/) vers les fichiers propres à chaque outil.

Source de vérité :  .agents/skills/        (skills, lus tels quels par Codex)
                    .agents/mcp/serveurs.json (serveurs MCP, sans secret)
Fichiers générés :  .claude/skills/        (copie pour Claude Code, versionnée pour marcher dès le clone)
                    .mcp.json              (MCP du projet pour Claude Code)
                    .codex/config.toml     (MCP du projet pour Codex)

Lancer :  python tools/agents/sync.py           (génère)
          python tools/agents/sync.py --check   (vérifie seulement, ne modifie rien ; code 1 s'il y a un écart)
"""
import filecmp
import json
import os
import re
import shutil
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENTS = os.path.join(RACINE, ".agents")
SKILLS_SRC = os.path.join(AGENTS, "skills")
SKILLS_CLAUDE = os.path.join(RACINE, ".claude", "skills")
SERVEURS = os.path.join(AGENTS, "mcp", "serveurs.json")
MCP_CLAUDE = os.path.join(RACINE, ".mcp.json")
MCP_CODEX = os.path.join(RACINE, ".codex", "config.toml")
MEMOIRE = os.path.join(AGENTS, "memoire")

ENTETE_TOML = "# Généré par tools/agents/sync.py depuis .agents/mcp/serveurs.json : ne pas modifier à la main.\n"


def _serveurs() -> dict:
    with open(SERVEURS, encoding="utf-8") as f:
        return json.load(f)["serveurs"]


def _mcp_claude(serveurs: dict) -> str:
    sortie = {}
    for nom, s in serveurs.items():
        env = dict(s.get("env", {}))
        for var in s.get("env_depuis_systeme", []):
            env[var] = "${" + var + "}"   # Claude Code remplace ${VAR} par la variable d'environnement
        sortie[nom] = {"type": "stdio", "command": s["command"], "args": s.get("args", []), "env": env}
    return json.dumps({"mcpServers": sortie}, indent=2, ensure_ascii=False) + "\n"


def _toml_str(v: str) -> str:
    return json.dumps(v, ensure_ascii=False)   # une chaîne JSON est une chaîne TOML valide


def _mcp_codex(serveurs: dict) -> str:
    lignes = [ENTETE_TOML]
    for nom, s in serveurs.items():
        lignes.append(f"\n[mcp_servers.{_toml_str(nom)}]")
        lignes.append(f"command = {_toml_str(s['command'])}")
        lignes.append("args = [" + ", ".join(_toml_str(a) for a in s.get("args", [])) + "]")
        if s.get("env"):
            lignes.append("env = { " + ", ".join(f"{_toml_str(k)} = {_toml_str(v)}" for k, v in s["env"].items()) + " }")
        if s.get("env_depuis_systeme"):
            # Codex transmet ces variables de l'environnement au serveur
            lignes.append("env_vars = [" + ", ".join(_toml_str(v) for v in s["env_depuis_systeme"]) + "]")
    return "\n".join(lignes) + "\n"


def _lire(chemin: str):
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def _ecrire(chemin: str, contenu: str, check: bool, ecarts: list) -> None:
    if _lire(chemin) == contenu:
        return
    ecarts.append(os.path.relpath(chemin, RACINE))
    if not check:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu)


def _skills_identiques() -> bool:
    if not os.path.isdir(SKILLS_CLAUDE):
        return False
    def pareil(cmp: filecmp.dircmp) -> bool:
        if cmp.left_only or cmp.right_only or cmp.funny_files:
            return False
        _, diff, err = filecmp.cmpfiles(cmp.left, cmp.right, cmp.common_files, shallow=False)
        if diff or err:
            return False
        return all(pareil(sous) for sous in cmp.subdirs.values())
    return pareil(filecmp.dircmp(SKILLS_SRC, SKILLS_CLAUDE))


def _verifier_memoire(avertissements: list) -> None:
    index = _lire(os.path.join(MEMOIRE, "INDEX.md")) or ""
    liens = set(re.findall(r"\]\(([^)]+\.md)\)", index))
    for nom in sorted(os.listdir(MEMOIRE)):
        if nom.endswith(".md") and nom != "INDEX.md" and nom not in liens:
            avertissements.append(f"note mémoire sans ligne dans INDEX.md : {nom}")
    for lien in sorted(liens):
        if not os.path.exists(os.path.join(MEMOIRE, lien)):
            avertissements.append(f"INDEX.md pointe vers une note absente : {lien}")


def main() -> int:
    check = "--check" in sys.argv
    ecarts: list = []
    avertissements: list = []

    serveurs = _serveurs()
    _ecrire(MCP_CLAUDE, _mcp_claude(serveurs), check, ecarts)
    _ecrire(MCP_CODEX, _mcp_codex(serveurs), check, ecarts)

    if not _skills_identiques():
        ecarts.append(".claude/skills/")
        if not check:
            shutil.rmtree(SKILLS_CLAUDE, ignore_errors=True)
            shutil.copytree(SKILLS_SRC, SKILLS_CLAUDE)

    for requis in ("ETAT.md", os.path.join("memoire", "INDEX.md")):
        if not os.path.exists(os.path.join(AGENTS, requis)):
            avertissements.append(f"fichier manquant : .agents/{requis}")
    _verifier_memoire(avertissements)
    for s in serveurs.values():
        for var in s.get("env_depuis_systeme", []):
            if not os.environ.get(var):
                avertissements.append(f"variable d'environnement absente : {var} (le MCP qui en a besoin ne marchera pas)")

    verbe = "à mettre à jour" if check else "mis à jour"
    for e in ecarts:
        print(f"{verbe} : {e}")
    for a in avertissements:
        print(f"attention : {a}")
    if not ecarts and not avertissements:
        print("tout est synchronisé.")
    return 1 if (check and ecarts) else 0


if __name__ == "__main__":
    sys.exit(main())
