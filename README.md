# My-Dev-Environment

A configurable Docker-based development environment with language toolchains, selectable editors, and optional AI coding assistants.

## Prerequisites

Install the following tools on your host:

- Docker Engine or Docker Desktop with Docker Compose v2
- Git
- curl
- Python 3

## Install without cloning the full repository

The standalone installer downloads only the setup script first. It then opens an interactive terminal UI (TUI) where you can select the development tools and editor you want.

While this feature is under review, run the installer from the feature branch:

```bash
curl -fsSL https://raw.githubusercontent.com/Augusto-Dantas/My-Dev-Environment/main/setup.sh -o /tmp/devbox-setup.sh
bash /tmp/devbox-setup.sh
```

The TUI lets you choose from these language toolchains:

| Profile | Included tools |
| --- | --- |
| Rust | rustup, stable toolchain, Cargo, rust-analyzer, Clippy, rustfmt |
| C/C++ | GCC, G++, Clang, clangd, clang-format, GDB, CMake, Ninja, Valgrind |
| Python | Python 3, pip, venv, development headers |
| Node.js / TypeScript | Node.js 22 and npm |
| Go | Go compiler and standard tools |
| Java | OpenJDK 17 |

You can also select one editor:

- **Neovim + NvChad**
- **Vim**
- **Helix**
- **No editor**

GitHub Copilot and CodeCompanion are optional integrations available when Neovim is selected.

After you confirm your choices, the installer performs a Git sparse checkout of only the files required to build the image: the Dockerfile, Compose file, Zsh configuration, and Neovim configuration. It does not download the full repository history or unrelated files. The Docker image is built on the first `devbox` invocation.

## Use the environment from any host directory

The installer creates a global launcher at:

```text
~/.local/bin/devbox
```

If that directory is not already in your `PATH`, add it:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

You can now enter the development environment from any project directory:

```bash
cd ~/projects/my-project
devbox
```

The current host directory is mounted into the container at `/workspace`. Each host directory gets its own Compose project and container, so different projects can use separate development environments. The container user is created with the host user's UID and GID to reduce file ownership issues in bind-mounted directories.

### Launcher commands

| Command | Description |
| --- | --- |
| `devbox --help` | Show all commands and usage information |
| `devbox` or `devbox shell` | Start the linked environment and open a Zsh shell |
| `devbox new` | Create a project with an interactive setup wizard |
| `devbox up` | Build (if needed) and start the linked container in the background |
| `devbox status` | Show the linked container status |
| `devbox logs` | Follow linked container logs |
| `devbox restart` | Rebuild and restart the linked container |
| `devbox down` | Stop and remove the linked container |

### Create a project

Run:

```bash
devbox new
```

The interactive wizard asks for the project name and language profile, whether to initialize Git, create a README, generate a language-appropriate `.gitignore`, and add an MIT license. You can also create a GitHub repository through the GitHub CLI (`gh`) if it is installed and authenticated.

Choose an existing registered development container or create a new one with a custom name. Projects linked to an existing container are created under that container's workspace directory. Container and project mappings are stored in your user configuration directory, not inside the generated project.

Use `devbox --help` at any time to see the available commands.

## AI coding assistants

### GitHub Copilot

Enable Copilot in the TUI. On the first Neovim launch, authenticate with:

```vim
:Copilot auth
```

Authentication is handled by GitHub inside Neovim.

### CodeCompanion

CodeCompanion adds AI chat, inline assistance, and action workflows to Neovim. It supports providers including OpenAI, Anthropic, Google Gemini, and Ollama.

Provider API keys are optional. When supplied during setup, they are stored in:

```text
~/.local/share/my-dev-environment/.env
```

The file is created with restricted permissions and is not part of the Git checkout. Never commit or share this file. Ollama can be configured to use a locally hosted model.

## Change your configuration

Run the installer again to choose a different set of language toolchains, editor, or AI integrations. Then, from the project directory where you want to apply the new image profile, run:

```bash
devbox restart
```

This rebuilds and restarts that directory's development container.

## Security notes

- Keep your local `.env` file private.
- Never paste API keys into source files, issues, or public logs.
- Revoke and replace any API key that may have been exposed.
- AI integrations are optional; the base development environment does not require provider credentials.
