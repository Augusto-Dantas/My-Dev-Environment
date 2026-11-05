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
EDITORS = [("nvim", "Neovim + NvChad"), ("vim", "Vim"), ("helix", "Helix"), ("none", "No editor")]

def tui(stdscr):
    curses.curs_set(0); stdscr.keypad(True)
    state={"langs":{x[0]:x[0]=="rust" for x in LANGUAGES},"editor":"nvim","copilot":False,"chat":False}
    rows=[("lang:"+k,v) for k,v in LANGUAGES]
    rows += [("editor:"+k,"Editor — "+v) for k,v in EDITORS]
    rows += [("copilot","GitHub Copilot — authenticate in Neovim after setup"),("chat","CodeCompanion — OpenAI, Anthropic, Gemini/Ollama")]
    cursor=0
    while True:
        stdscr.erase(); h,w=stdscr.getmaxyx()
        title=" MY DEV ENVIRONMENT · SETUP WIZARD "
        stdscr.addstr(1,max(0,(w-len(title))//2),title[:max(0,w-1)],curses.A_BOLD)
        stdscr.addstr(3,2,"↑/↓ Navigate · Space Select · Enter Confirm · q Quit"[:max(0,w-3)])
        stdscr.addstr(5,3,"LANGUAGE TOOLCHAINS AND EDITOR",curses.A_UNDERLINE)
        visible=max(1,h-9)
        start=max(0,min(cursor-visible+1,len(rows)-visible))
        for i in range(start,min(len(rows),start+visible)):
            ident,label=rows[i]; y=7+i-start
            if ident.startswith("lang:"): mark="[x]" if state["langs"][ident[5:]] else "[ ]"
            elif ident.startswith("editor:"): mark="(*)" if state["editor"]==ident[7:] else "( )"
            else: mark="[x]" if state[ident] else "[ ]"
            stdscr.addstr(y,4,(mark+" "+label)[:max(0,w-8)],curses.A_REVERSE if i==cursor else curses.A_NORMAL)
        stdscr.addstr(h-2,2,"Enter: Continue  |  q: Cancel"[:max(0,w-3)],curses.A_BOLD)
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
        if not shutil.which(tool): raise SystemExit(f"Missing required dependency: {tool}")
    print("Rust is selected by default. Choose language toolchains and an editor:")
    state=curses.wrapper(tui)
    if state is None: print("Setup cancelled."); return 1
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
      for key,label in (("OPENAI_API_KEY","OpenAI"),("ANTHROPIC_API_KEY","Anthropic"),("GEMINI_API_KEY","Google Gemini")):
        env[key]=getpass.getpass(label+" API key (press Enter to skip): ")
    root=Path(a.root).expanduser(); src=root/"source"
    root.mkdir(parents=True,exist_ok=True)
    if src.exists(): shutil.rmtree(src)
    subprocess.run(["git","clone","--filter=blob:none","--sparse","--depth","1","--branch",a.ref,a.repo,str(src)],check=True)
    subprocess.run(["git","-C",str(src),"sparse-checkout","set","--no-cone","Dockerfile","docker-compose.yml",".zshrc","nvim-config","devbox.py"],check=True)
    (root/".env").write_text("# Local Devbox configuration. Keep this file private.\n"+"".join(f"{k}={dotenv_quote(v)}\n" for k,v in env.items()),encoding="utf-8")
    (root/".env").chmod(0o600)
    bindir=Path(a.bin_dir).expanduser(); bindir.mkdir(parents=True,exist_ok=True)
    cli = bindir/"devbox.py"
    shutil.copy2(src/"devbox.py", cli)
    cli.chmod(0o755)
    wrapper=bindir/"devbox"
    wrapper.write_text("""#!/usr/bin/env bash
set -Eeuo pipefail
exec python3 "$(dirname "$0")/devbox.py" "$@"
""",encoding="utf-8")
    wrapper.chmod(0o755)

    path_entry = str(bindir.resolve())
    print(f"\nWould you like to add {path_entry} to your PATH permanently? [y/N] ", end="", flush=True)
    answer = input().strip().lower()
    if answer in ("y", "yes"):
        shell = Path(os.environ.get("SHELL", "")).name
        if shell == "zsh":
            rc = Path.home() / ".zshrc"
            path_line = f'export PATH="{path_entry}:$PATH"'
        elif shell == "fish":
            rc = Path.home() / ".config/fish/config.fish"
            path_line = f' fish_add_path "{path_entry}"'.lstrip()
        elif shell == "bash":
            rc = Path.home() / ".bashrc"
            path_line = f'export PATH="{path_entry}:$PATH"'
        else:
            rc = Path.home() / ".profile"
            path_line = f'export PATH="{path_entry}:$PATH"'
        rc.parent.mkdir(parents=True, exist_ok=True)
        existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
        if path_line not in existing:
            with rc.open("a", encoding="utf-8") as config:
                if existing and not existing.endswith("\\n"):
                    config.write("\\n")
                config.write(f"\\n# My Dev Environment CLI\\n{path_line}\\n")
        print(f"Added {path_entry} to PATH in {rc}.")
        print("Open a new terminal or reload the shell configuration to use devbox.")
    else:
        print("Skipped PATH configuration. You can add ~/.local/bin to PATH later.")

    print("\\nSetup complete. Change to any project directory and run: devbox")
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        command = " ".join(str(part) for part in exc.cmd)
        raise SystemExit(f"Setup failed while running: {command} (exit code {exc.returncode}). Check the error above and try again.")
