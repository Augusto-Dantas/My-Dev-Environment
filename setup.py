#!/usr/bin/env python3
"""Standalone installer: sparse-checkout only the files required for the image."""
from __future__ import annotations
import argparse, curses, getpass, os, shutil, subprocess
from pathlib import Path

LANGUAGES = [
    ("rust", "Rust — rustup, Cargo, rust-analyzer, Clippy, rustfmt"),
    ("cpp", "C/C++ — GCC, Clang, GDB, CMake, Ninja, clangd"),
    ("python", "Python — Python 3, pip, venv, headers"),
    ("node", "Node.js/TypeScript — Node 22 and npm"),
    ("go", "Go — compiler and standard tools"),
    ("java", "Java — OpenJDK 17"),
]
EDITORS = [("nvim", "Neovim + NvChad"), ("vim", "Vim"), ("helix", "Helix"), ("none", "Sem editor")]

def tui(stdscr):
    curses.curs_set(0); stdscr.keypad(True)
    state={"langs":{x[0]:x[0]=="rust" for x in LANGUAGES},"editor":"nvim","copilot":False,"chat":False}
    rows=[("lang:"+k,v) for k,v in LANGUAGES]
    rows += [("editor:"+k,"Editor — "+v) for k,v in EDITORS]
    rows += [("copilot","GitHub Copilot — autenticação posterior no Neovim"),("chat","CodeCompanion — OpenAI, Anthropic, Gemini/Ollama")]
    cursor=0
    while True:
        stdscr.erase(); h,w=stdscr.getmaxyx()
        title=" MY DEV ENVIRONMENT · INSTALADOR "
        stdscr.addstr(1,max(0,(w-len(title))//2),title[:max(0,w-1)],curses.A_BOLD)
        stdscr.addstr(3,2,"↑/↓ navegar · Espaço selecionar · Enter confirmar · q cancelar"[:max(0,w-3)])
        stdscr.addstr(5,3,"PACOTES E EDITOR",curses.A_UNDERLINE)
        visible=max(1,h-9)
        start=max(0,min(cursor-visible+1,len(rows)-visible))
        for i in range(start,min(len(rows),start+visible)):
            ident,label=rows[i]; y=7+i-start
            if ident.startswith("lang:"): mark="[x]" if state["langs"][ident[5:]] else "[ ]"
            elif ident.startswith("editor:"): mark="(*)" if state["editor"]==ident[7:] else "( )"
            else: mark="[x]" if state[ident] else "[ ]"
            stdscr.addstr(y,4,(mark+" "+label)[:max(0,w-8)],curses.A_REVERSE if i==cursor else curses.A_NORMAL)
        stdscr.addstr(h-2,2,"Enter: continuar  |  q: cancelar"[:max(0,w-3)],curses.A_BOLD)
        stdscr.refresh(); key=stdscr.getch()
        if key in (curses.KEY_UP,ord("k")): cursor=(cursor-1)%len(rows)
        elif key in (curses.KEY_DOWN,ord("j")): cursor=(cursor+1)%len(rows)
        elif key==ord(" "):
            ident=rows[cursor][0]
            if ident.startswith("lang:"): state["langs"][ident[5:]]=not state["langs"][ident[5:]]
            elif ident.startswith("editor:"): state["editor"]=ident[7:]
            else: state[ident]=not state[ident]
        elif key in (10,13,curses.KEY_ENTER): return state
        elif key in (ord("q"),27): return None

def dotenv_quote(v):
    return "'" + v.replace("\\","\\\\").replace("'","\\'") + "'"

def main():
    p=argparse.ArgumentParser()
    for name in ("root","repo","ref","bin-dir"): p.add_argument("--"+name,required=True)
    a=p.parse_args()
    for tool in ("git","docker","curl"):
        if not shutil.which(tool): raise SystemExit(f"Dependência ausente: {tool}")
    print("Rust vem pré-selecionado. Escolha pacotes e editor:")
    state=curses.wrapper(tui)
    if state is None: print("Instalação cancelada."); return 1
    editor=state["editor"]
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
      "DEVBOX_UID":str(os.getuid()),"DEVBOX_GID":str(os.getgid()),
    }
    if env["ENABLE_CODECOMPANION"]=="1":
      for key,label in (("OPENAI_API_KEY","OpenAI"),("ANTHROPIC_API_KEY","Anthropic"),("GEMINI_API_KEY","Gemini")):
        env[key]=getpass.getpass(label+" API key (Enter para ignorar): ")
    root=Path(a.root).expanduser(); src=root/"source"
    root.mkdir(parents=True,exist_ok=True)
    if src.exists(): shutil.rmtree(src)
    subprocess.run(["git","clone","--filter=blob:none","--sparse","--depth","1","--branch",a.ref,a.repo,str(src)],check=True)
    subprocess.run(["git","-C",str(src),"sparse-checkout","set","Dockerfile","docker-compose.yml",".zshrc","nvim-config"],check=True)
    (root/".env").write_text("# Configuração local do Devbox. Não compartilhar.\n"+"".join(f"{k}={dotenv_quote(v)}\n" for k,v in env.items()),encoding="utf-8")
    (root/".env").chmod(0o600)
    bindir=Path(a.bin_dir).expanduser(); bindir.mkdir(parents=True,exist_ok=True)
    wrapper=bindir/"devbox"
    wrapper.write_text("""#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${DEVBOX_HOME:-$HOME/.local/share/my-dev-environment}"
COMPOSE="$ROOT/source/docker-compose.yml"
WORKSPACE="$(pwd -P)"
ID="$(printf '%s' "$WORKSPACE" | sha256sum | cut -c1-10)"
PROJECT="devbox-$ID"
export DEVBOX_WORKSPACE="$WORKSPACE" DEVBOX_CONTAINER_NAME="devbox-$ID"
dc=(docker compose --env-file "$ROOT/.env" -f "$COMPOSE" --project-directory "$ROOT/source" -p "$PROJECT")
case "${1:-shell}" in
  up) "${dc[@]}" up -d --build ;;
  down) "${dc[@]}" down ;;
  restart) "${dc[@]}" up -d --build --force-recreate ;;
  status|ps) "${dc[@]}" ps ;;
  logs) "${dc[@]}" logs -f ;;
  shell|sh) "${dc[@]}" up -d && "${dc[@]}" exec devenv zsh ;;
  *) echo "Uso: devbox [shell|up|down|restart|status|logs]"; exit 2 ;;
esac
""",encoding="utf-8")
    wrapper.chmod(0o755)
    print("\nInstalação pronta. Adicione ~/.local/bin ao PATH se necessário.")
    print("Entre em qualquer diretório de projeto e execute: devbox")
    return 0

if __name__=="__main__": raise SystemExit(main())
