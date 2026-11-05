# My-Dev-Environment

A ready-to-use development environment powered by Docker, Zsh, Neovim, and NvChad, with optional AI coding assistants.

## Requirements

- Git
- Docker Engine or Docker Desktop with Docker Compose v2
- An interactive terminal

## Quick start

Clone the repository, enter it, and run the setup wizard **before building the container**:

```bash
git clone https://github.com/Augusto-Dantas/My-Dev-Environment.git
cd My-Dev-Environment
bash setup.sh
docker compose up -d --build
docker compose exec devenv zsh
```

The setup wizard creates a private local `.env` file. It lets you enable AI integrations and optionally enter provider API keys. The file is excluded from Git. You can also edit `.env` manually using `.env.example` as a template.

## AI assistants

### GitHub Copilot

Enable it in the setup wizard. On the first Neovim launch, authenticate with:

```vim
:Copilot auth
```

Copilot authentication is performed interactively by GitHub; no token is stored by the setup wizard.

### CodeCompanion

Enable CodeCompanion in the wizard to add an AI chat, inline assistant, and action palette. It supports configuring providers such as OpenAI, Anthropic, Google Gemini, and local Ollama models. Set the matching API key in `.env` (or configure Ollama in your Neovim CodeCompanion adapter settings).

Keymaps:
- `<leader>aa`: AI actions
- `<leader>ac`: toggle AI chat
- `<leader>ai`: inline assistant

Provider keys are optional at setup time and should only be supplied for services you use.

## Useful commands

Run these from the project directory:

| Command | Description |
| --- | --- |
| `docker compose exec devenv zsh` | Open another shell in the container |
| `docker compose down` | Stop and remove the container |
| `docker compose build --no-cache devenv` | Rebuild the image from scratch |
| `docker compose logs -f devenv` | Follow container logs |

Your files in `./workspace` are available inside the container at `/workspace`. Neovim data and Cargo registry data are persisted in Docker volumes.

## Security

- Never commit `.env` or paste API keys into issues or chat.
- Rotate a key immediately if it is accidentally exposed.
- AI integrations are opt-in; with both options disabled, the base environment works as before.
