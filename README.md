# My-Dev-Environment

A ready-to-use development environment powered by Docker, Zsh, Neovim, and NvChad.

## Requirements

- Git
- Docker Engine or Docker Desktop
- Docker Compose v2

## Quick start

Copy and paste this single command into your terminal:

```bash
git clone https://github.com/Augusto-Dantas/My-Dev-Environment.git && cd My-Dev-Environment && docker compose up -d --build && docker compose exec devenv zsh
```

That's it. Docker builds the image, starts the development container, and opens a Zsh shell inside it.

## Useful commands

Run these from the project directory:

| Command | Description |
| --- | --- |
| `docker compose exec devenv zsh` | Open another shell in the container |
| `docker compose down` | Stop and remove the container |
| `docker compose build --no-cache devenv` | Rebuild the image from scratch |
| `docker compose logs -f devenv` | Follow container logs |

Your files in `./workspace` are available inside the container at `/workspace`. Neovim data and Cargo registry data are persisted in Docker volumes.
