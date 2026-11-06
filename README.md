# My-Dev-Environment

A configurable, Docker-based development environment with selectable language toolchains, terminal editors, a browser-based graphical editor, and optional AI coding assistants.

## Requirements

Install these tools on the host:

- Docker Engine or Docker Desktop with Docker Compose v2
- Git
- GitHub CLI (`gh`) — [installation instructions](https://github.com/cli/cli#installation)
- `curl`
- Python 3 with `venv` support (`python3-venv` on Debian/Ubuntu)

The installer checks that all five dependencies are available before continuing. Authenticate the GitHub CLI with:

```bash
gh auth login
```

Authentication is needed for authenticated GitHub operations, such as creating and publishing repositories. The CLI is also used to retrieve project license texts.

## Install

The installer downloads a small setup script and then opens an interactive terminal wizard. It does not require you to clone the full repository.

```bash
curl -fsSL https://raw.githubusercontent.com/Augusto-Dantas/My-Dev-Environment/main/setup.sh -o /tmp/devbox-setup.sh
DEVBOX_REF=main bash /tmp/devbox-setup.sh
```

To install non-interactively from a saved YAML configuration, pass `--config`:

```bash
DEVBOX_REF=main bash /tmp/devbox-setup.sh --config ./devbox.yaml
```

The installer automatically creates an isolated Python virtual environment for its YAML parser (PyYAML); it does not modify your system Python packages. If you use a custom configuration file, keep it in your project or another backed-up location so it can be reused.

Use the arrow keys to navigate, **Space** to toggle options, **Enter** to confirm, and **q** to cancel.

### Language toolchains

Select one or more language profiles:

| Profile | Included tools |
| --- | --- |
| Rust | rustup, stable toolchain, Cargo, rust-analyzer, Clippy, rustfmt |
| C/C++ | GCC, G++, Clang, clangd, clang-format, GDB, CMake, Ninja, Valgrind |
| Python | Python 3, pip, venv, development headers |
| Node.js / TypeScript | Node.js 22 and npm |
| Go | Go compiler and standard tools |
| Java | OpenJDK 17 |

Rust is selected by default. You can change the selection in the wizard.

### Editors

Choose one or more editors. These are the currently supported options:

| Editor | Type | Notes |
| --- | --- | --- |
| Neovim + NvChad | Terminal | Neovim configuration is included |
| Vim | Terminal | Basic Vim configuration |
| Helix | Terminal | Basic Helix configuration |
| Emacs | Terminal | Installed as `emacs-nox` |
| Micro | Terminal | Lightweight terminal editor |
| code-server | Graphical, browser-based | VS Code-like interface accessible through a web browser |

The first selected editor is used as the default for `$EDITOR`. You can still launch other selected terminal editors directly inside the container.

To use the graphical editor, select **code-server** during installation, start the environment, and run:

```bash
devbox gui
```

Then open [http://localhost:8080](http://localhost:8080) in your browser. The generated access password is stored in the private Devbox environment file at `~/.local/share/my-dev-environment/.env`. The service is published on localhost, not on all host network interfaces.

GitHub Copilot and CodeCompanion are optional Neovim integrations. They are only enabled when Neovim is selected. CodeCompanion supports providers such as OpenAI, Anthropic, Google Gemini, and Ollama; provider credentials are optional.

After you confirm your selections, the installer performs a shallow Git sparse checkout of the files needed to build the development image. The Docker image is built when you first start a Devbox environment.

### Save and reuse YAML configuration

The repository includes [`devbox.yaml`](./devbox.yaml) as a complete example. It records language profiles, multiple editors, AI assistant toggles, and startup commands.

To save the selections from the interactive wizard to a YAML file:

```bash
DEVBOX_REF=main bash /tmp/devbox-setup.sh --save-config ./devbox.yaml
```

Edit the resulting file to add startup commands, then reuse it with `--config`. The supported schema is:

```yaml
version: 1
languages: [rust, python, node]
editors: [nvim, helix, code-server]
assistants:
  copilot: true
  codecompanion: false
startup:
  commands:
    - "mkdir -p /workspace/.cache"
    - "if [ -f package.json ]; then npm install; fi"
```

Supported language IDs: `rust`, `cpp`, `python`, `node`, `go`, and `java`. Supported editor IDs: `nvim`, `vim`, `helix`, `emacs`, `micro`, and `code-server`. The first editor listed becomes the default for `$EDITOR`.

Commands in `startup.commands` are written to the private installation startup script and run as the unprivileged `developer` user whenever the container starts. They run from `/workspace`; make them idempotent because they may execute repeatedly. Only load YAML files and startup commands that you trust: startup commands execute shell code inside your development container.

## Use Devbox

The installer places the launcher at:

```text
~/.local/bin/devbox
```

If `~/.local/bin` is not already in your `PATH`, add it to your shell configuration:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Open a new terminal or reload the shell configuration, then run Devbox from any project directory:

```bash
cd ~/projects/my-project
devbox
```

The current host directory is mounted into the container at `/workspace`. Each host directory gets its own Compose project and container. The container user is created with the host user's UID and GID to reduce file ownership issues in bind-mounted directories.

### Commands

| Command | Description |
| --- | --- |
| `devbox --help` | Show commands and usage information |
| `devbox` or `devbox shell` | Start the linked environment and open a Zsh shell |
| `devbox new` | Create a project with the interactive project wizard |
| `devbox up` | Build (if needed) and start the linked container in the background |
| `devbox status` | Show the linked container status |
| `devbox logs` | Follow linked container logs |
| `devbox gui` | Start code-server in the linked container |
| `devbox restart` | Rebuild and restart the linked container |
| `devbox down` | Stop and remove the linked container |
| `devbox --uninstall` | Uninstall Devbox after explicit confirmation |

### Create a project

Run:

```bash
devbox new
```

The wizard asks for a project name and language profile, then lets you choose whether to:

- Initialize a Git repository
- Create a `README.md`
- Generate a language-appropriate `.gitignore`
- Add a license retrieved from GitHub using `gh repo license view`
- Create a GitHub repository and push the initial commit using `gh`

The available license identifiers are MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, and MPL-2.0. The GitHub CLI must be installed to retrieve a license. To create or publish a GitHub repository, authenticate first with `gh auth login`.

You can link the project to an existing registered development container or create a new container with a custom name. Project and container mappings are stored in your user configuration directory (`~/.config/my-dev-environment` by default), not inside the generated project.

### Uninstall

Run:

```bash
devbox --uninstall
```

The command explains what will be removed and requires you to type `UNINSTALL` to authorize the operation. It removes the Devbox launcher, CLI, downloaded installation files (including the local `.env`), and Devbox user mappings.

It does **not** delete project directories, stop or remove Docker containers, or delete Docker volumes. If your user account lacks permission to remove an installation file, the command reports the failure; correct the file ownership or permissions before retrying. The uninstall command does not automatically invoke `sudo`.

## Change your configuration

Run the installer again to select a different set of language toolchains, editors, or AI integrations. Then, from a project directory, run:

```bash
devbox restart
```

This rebuilds and restarts that directory's development container using the updated configuration.

## Security notes

- Keep the local Devbox `.env` file private; it may contain API keys and the code-server password.
- Never commit or share API keys, passwords, or private environment files.
- Revoke and replace any credential that may have been exposed.
- AI integrations are optional; the base development environment does not require provider credentials.
