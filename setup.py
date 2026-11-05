#!/usr/bin/env python3
"""Standalone installer: only sparse-checkouts the files required to build the image."""
from __future__ import annotations
import argparse
import curses
import getpass
import os
import shutil
import subprocess
from pathlib import Path

LANGUAGES = [
    ("rust", "Rust", "rustup, cargo, rust-analyzer, clippy, rustfmt"),
    ("cpp", "C / C++", "GCC, Clang, GDB, CMake, Ninja, clangd, clang-format"),
    ("python", "Python", "Python 3, pip, venv, headers"),
    ("node", "Node.js / TypeScript", "Node.js 22 and npm"),
    ("go", "Go", "Go compiler and standard tools"),
    ("java", "Java", "OpenJDK 17"),
]
EDITORS = [("nvim", "Neovim + NvChad"), ("vim", "Vim"), ("helix", "Helix"), ("none", "Sem editor")]

def tui(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    state = {"langs": {x[0]: x[0] == "rust" for x in LANGUAGES}, "editor": 0, "copilot": False, "chat": False}
    rows = [("lang:" + x[0], x[1], x[2]) for x in LANGUAGES]
    rows += [("editor:" + x[0], "Editor: " + x[1], "Seleciona o editor principal do container") for x in EDITORS]
    rows += [("copilot", "GitHub Copilot", "Autenticação posterior pelo Neovim"), ("chat", "CodeCompanion", "OpenAI, Anthropic, Gemini ou Ollama")]
    cursor = 0
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        title = " MY DEV ENVIRONMENT — INSTALADOR "
        stdscr.addstr(1, max(0, (w-len(title))//2), title[:max(0,w-1)], curses.A_BOLD)
        stdscr.addstr(3, 2, "↑/↓ navegar · Espaço selecionar · Enter confirmar · q cancelar"[:max(0,w-3)])
        stdscr.addstr(5, 3, "PACOTES DE DESENVOLVIMENTO", curses.A_UNDERLINE)
        for i, (key, label, desc) in enumerate(rows):
            y = 7 + i*2
            if y >= h-3: break
            if key.startswith("lang:"):
                mark = "[x]" if state["langs"][key[5:]] else "[ ]"
            elif key.startswith("editor:"):
                mark = "(*)" if EDITORS[state["editor"]][0] == key[7:] else "( )"
            else:
                mark = "[x]" if state[key] else "[ ]"
            stdscr.addstr(y, 4, f"{mark} {label}"[:max(0,w-8)], curses.A_REVERSE if i == cursor else curses.A_NORMAL)
            if y+1 < h-2:
                stdscr.addstr(y+1, 8, desc[:max(0,w-12)], curses.A_DIM)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")): cursor = (cursor-1) % len(rows)
        elif key in (curses.KEY_DOWN, ord("j")): cursor = (cursor+1) % len(rows)
        elif key == ord(" "):
            ident = rows[cursor][0]
            if ident.startswith("lang:"):
                name = ident[5:]; state["langs"][name] = not state["langs"][name]
            elif ident.startswith("editor:"):
                state["editor"] = next(i for i,x in enumerate(EDITORS) if x[0] == ident[7:])
            else: state[ident] = not state[ident]
        elif key in (10,13,curses.KEY_ENTER): return state
        elif key in (ord("q"),27): return None

def quote(value):
    return '"' + value.replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('`','\\`') + '"'

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True); p.add_argument("--repo",required=True); p.add_argument("--ref",required=True); p.add_argument("--bin-dir",required=True)
    a=p.parse_args(); root=Path(a.root).expanduser(); src=root/"source"
    if not shutil.which("git") or not shutil.which("docker") or not shutil.which("curl"):
        raise SystemExit("Instale Git, Docker Compose v2 e curl antes de continuar.")
    print("Selecione os pacotes e o editor. O Rust vem pré-selecionado como exemplo.")
    state=curses.wrapper(tui)
    if state is None: print("Instalação cancelada."); return 1
    editor=EDITORS[state["editor"]][0]
    env={
      "EDITOR_CHOICE":editor,
      "INSTALL_RUST":"1" if state["langs"]["rust"] else "0",
      "INSTALL_CPP":"1" if state["langs"]["cpp"] else "0",
      "INSTALL_PYTHON":"1" if state["langs"]["python"] else "0",
      "INSTALL_NODE":"1" if state["langs"]["node"] else "0",
      "INSTALL_GO":"1" if state["langs"]["go"] else "0",
      "INSTALL_JAVA":"1" if state["langs"]["java"] else "0",
      "ENABLE_COPILOT":"1" if state["copilot"] and editor=="nvim" else "0",
      "ENABLE_CODECOMPANION":"1" if state["chat"] and editor=="nvim" else "0",
    }
    secrets={}
    if env["ENABLE_CODECOMPANION"]=="1":
      for key,label in [("OPENAI_API_KEY","OpenAI"),("ANTHROPIC_API_KEY","Anthropic"),("GEMINI_API_KEY","Gemini")]:
        secrets[key]=getpass.getpass(f"{label} API key (Enter para ignorar): ")
    env.update(secrets)
    root.mkdir(parents=True,exist_ok=True)
    if src.exists(): shutil.rmtree(src)
    subprocess.run(["git","clone","--filter=blob:none","--sparse","--depth","1","--branch",a.ref,a.repo,str(src)],check=True)
    subprocess.run(["git","-C",str(src),"sparse-checkout","set","Dockerfile","docker-compose.yml",".zshrc","nvim-config"],check=True)
    envfile=root/".env"
    envfile.write_text("# Gerado pelo instalador. Contém apenas configurações locais.\n"+"".join(f"{k}={quote(v)}\n" for k,v in env.items()),encoding="utf-8")
    envfile.chmod(0o600)
    bin_dir=Path(a.bin_dir).expanduser(); bin_dir.mkdir(parents=True,exist_ok=True)
    wrapper=bin_dir/"devbox"
    wrapper.write_text("""#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${DEVBOX_HOME:-$HOME/.local/share/my-dev-environment}"
COMPOSE="$ROOT/source/docker-compose.yml"
WORKSPACE="$(pwd -P)"
ID="$(printf '%s' "$WORKSPACE" | sha256sum | cut -c1-10)"
PROJECT="devbox-$ID"
export DEVBOX_WORKSPACE="$WORKSPACE" DEVBOX_CONTAINER_NAME="devbox-$ID"
case "${1:-shell}" in
  up) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" up -d --build ;;
  down) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" down ;;
  restart) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" up -d --build --force-recreate ;;
  status|ps) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" ps ;;
  logs) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" logs -f ;;
  shell|sh) docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" up -d && docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT" exec devenv zsh ;;
  *) echo "Uso: devbox [shell|up|down|restart|status|logs]"; exit 2 ;;
esac
""",encoding="utf-8")
    wrapper.chmod(0o755)
    print("\nInstalação configurada. O build será feito na primeira execução do devbox.")
    print(f"Comando instalado em: {wrapper}")
    if str(bin_dir) not in os.environ.get("PATH","").split(os.pathsep):
      print(f"Adicione ao PATH: export PATH=\"{bin_dir}:$PATH\"")
    print("Entre em qualquer diretório e execute: devbox")
    return 0

if __name__=="__main__": raise SystemExit(main())
