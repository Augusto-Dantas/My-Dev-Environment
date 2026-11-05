#!/usr/bin/env python3
"""Interactive pre-build setup for My-Dev-Environment (stdlib only)."""
from __future__ import annotations

import curses
import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OPTIONS = [
    ("copilot", "GitHub Copilot", "Inline completions; authenticate later with :Copilot auth"),
    ("codecompanion", "CodeCompanion", "AI chat, inline assistant and actions"),
    ("openai", "OpenAI API key", "Optional; used by CodeCompanion"),
    ("anthropic", "Anthropic API key", "Optional; used by CodeCompanion"),
    ("gemini", "Google Gemini API key", "Optional; used by CodeCompanion"),
]
selected = {"copilot": False, "codecompanion": False, "openai": False, "anthropic": False, "gemini": False}


def draw(stdscr, cursor):
    curses.curs_set(0)
    stdscr.keypad(True)
    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        title = " MY DEV ENVIRONMENT — CONFIGURAÇÃO "
        stdscr.addstr(1, max(0, (width - len(title)) // 2), title[: max(0, width - 1)], curses.A_BOLD)
        stdscr.addstr(3, 2, "Use ↑/↓ para navegar, Espaço para marcar, Enter para continuar, q para sair.")
        stdscr.addstr(5, 4, "INTEGRAÇÕES E PROVEDORES", curses.A_UNDERLINE)
        for i, (key, label, description) in enumerate(OPTIONS):
            y = 7 + i * 3
            if y + 1 >= height - 3:
                break
            marker = "[x]" if selected[key] else "[ ]"
            attr = curses.A_REVERSE if i == cursor else curses.A_NORMAL
            stdscr.addstr(y, 4, f"{marker} {label}"[: max(0, width - 8)], attr)
            stdscr.addstr(y + 1, 8, description[: max(0, width - 12)], curses.A_DIM)
        footer = "Enter: salvar e continuar   q: cancelar"
        stdscr.addstr(height - 2, 2, footer[: max(0, width - 3)], curses.A_BOLD)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            cursor = (cursor - 1) % len(OPTIONS)
        elif key in (curses.KEY_DOWN, ord("j")):
            cursor = (cursor + 1) % len(OPTIONS)
        elif key == ord(" "):
            k = OPTIONS[cursor][0]
            selected[k] = not selected[k]
            if k in ("openai", "anthropic", "gemini") and selected[k]:
                selected["codecompanion"] = True
        elif key in (10, 13, curses.KEY_ENTER):
            return True
        elif key in (ord("q"), 27):
            return False


def dotenv_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> int:
    try:
        accepted = curses.wrapper(draw, 0)
    except curses.error:
        print("Este assistente precisa de um terminal interativo com suporte a curses.")
        return 2
    if not accepted:
        print("Configuração cancelada; nenhum arquivo foi alterado.")
        return 1

    secrets = {}
    if selected["codecompanion"]:
        for key, label in (
            ("OPENAI_API_KEY", "OpenAI"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("GEMINI_API_KEY", "Google Gemini"),
        ):
            if selected[key.lower().replace("_api_key", "")]:
                secrets[key] = getpass.getpass(f"{label} API key (Enter para ignorar): ")

    values = {
        "ENABLE_COPILOT": "1" if selected["copilot"] else "0",
        "ENABLE_CODECOMPANION": "1" if selected["codecompanion"] else "0",
        "OPENAI_API_KEY": secrets.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": secrets.get("ANTHROPIC_API_KEY", ""),
        "GEMINI_API_KEY": secrets.get("GEMINI_API_KEY", ""),
    }
    env = "# Gerado por setup.py; nao compartilhe nem versione este arquivo.\n"
    env += "".join(f"{key}={dotenv_quote(value)}\n" for key, value in values.items())
    path = ROOT / ".env"
    path.write_text(env, encoding="utf-8")
    path.chmod(0o600)
    print("\nConfiguração salva em .env (permissão 600).")
    print("Próximo passo: docker compose up -d --build")
    print("Depois: docker compose exec devenv zsh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
