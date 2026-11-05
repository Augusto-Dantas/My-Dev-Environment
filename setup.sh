#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -t 0 ]]; then
  echo "Execute este assistente em um terminal interativo: bash setup.sh" >&2
  exit 1
fi

clear 2>/dev/null || true
cat <<'BANNER'
╭──────────────────────────────────────────────────────────────╮
│                 MY DEV ENVIRONMENT · SETUP                   │
│             Assistente de configuração pré-build             │
╰──────────────────────────────────────────────────────────────╯
BANNER

ask_yes_no() {
  local prompt="$1" default="${2:-y}" answer
  while true; do
    if [[ "$default" == "y" ]]; then
      read -r -p "$prompt [S/n]: " answer
      answer="${answer:-s}"
    else
      read -r -p "$prompt [s/N]: " answer
      answer="${answer:-n}"
    fi
    case "$answer" in
      s|S|sim|SIM|y|Y|yes|YES) return 0 ;;
      n|N|nao|não|NAO|NÃO|no|NO) return 1 ;;
      *) echo "Responda s ou n." ;;
    esac
  done
}

read_secret() {
  local prompt="$1" value
  read -r -s -p "$prompt (Enter para ignorar): " value
  printf '\n' >&2
  printf '%s' "$value"
}

echo
echo "Escolha os assistentes que deseja habilitar:"
ENABLE_COPILOT=0
ENABLE_CODECOMPANION=0
ask_yes_no "Habilitar GitHub Copilot (autenticação pelo comando :Copilot auth)?" y && ENABLE_COPILOT=1 || true
ask_yes_no "Habilitar CodeCompanion (OpenAI, Anthropic, Gemini ou Ollama)?" y && ENABLE_CODECOMPANION=1 || true

OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
GEMINI_API_KEY=""
if [[ "$ENABLE_CODECOMPANION" == "1" ]]; then
  echo
  echo "Chaves são opcionais e serão gravadas apenas no .env local (ignorado pelo Git)."
  ask_yes_no "Configurar chave OpenAI agora?" n && OPENAI_API_KEY="$(read_secret "OPENAI_API_KEY")" || true
  ask_yes_no "Configurar chave Anthropic agora?" n && ANTHROPIC_API_KEY="$(read_secret "ANTHROPIC_API_KEY")" || true
  ask_yes_no "Configurar chave Google Gemini agora?" n && GEMINI_API_KEY="$(read_secret "GEMINI_API_KEY")" || true
fi

umask 077
cat > .env <<EOF
# Gerado por setup.sh. Não compartilhe este arquivo.
ENABLE_COPILOT=$ENABLE_COPILOT
ENABLE_CODECOMPANION=$ENABLE_CODECOMPANION
OPENAI_API_KEY=$OPENAI_API_KEY
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
GEMINI_API_KEY=$GEMINI_API_KEY
EOF
chmod 600 .env

echo
echo "Configuração salva em .env."
echo "Próximo passo: docker compose up -d --build"
echo "Depois: docker compose exec devenv zsh"
