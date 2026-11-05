# My-Dev-Environment

Ambiente de desenvolvimento Docker configurável: linguagens, toolchains, editor e integrações de IA.

## Instalar sem clonar o repositório completo

Requisitos no host: Docker Engine/Desktop com Compose v2, Git, curl e Python 3.

Enquanto a implementação estiver em revisão, use a branch de desenvolvimento:

```bash
curl -fsSL https://raw.githubusercontent.com/Augusto-Dantas/My-Dev-Environment/feat/ai-integrations-tui-setup/setup.sh -o /tmp/devbox-setup.sh && bash /tmp/devbox-setup.sh
```

O instalador é independente e baixa somente o script Python. A TUI permite selecionar:
- Rust (rustup, Cargo, rust-analyzer, Clippy e rustfmt)
- C/C++ (GCC, Clang, GDB, CMake, Ninja, clangd e clang-format)
- Python, Node.js/TypeScript, Go e Java
- Editor: Neovim + NvChad, Vim, Helix ou nenhum
- GitHub Copilot e CodeCompanion (opcionais; apenas com Neovim)

Depois das escolhas, ele faz *sparse checkout* de apenas Dockerfile, Compose, zshrc e configuração do Neovim. O histórico e arquivos não usados não são baixados. A imagem só é construída na primeira execução do comando global.

## Usar em qualquer diretório do host

O instalador cria `~/.local/bin/devbox`. Se necessário, adicione ao PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Agora, de qualquer diretório:

```bash
cd ~/projetos/meu-projeto
devbox
```

O diretório atual é montado no container como `/workspace`. Cada caminho recebe um container separado, e o usuário do container usa o UID/GID do host para reduzir problemas de permissão nos arquivos montados.

Comandos: `devbox up`, `devbox shell`, `devbox status`, `devbox logs`, `devbox restart`, `devbox down`.

## IA

Copilot: autentique no Neovim com `:Copilot auth`. CodeCompanion oferece chat e ações para provedores OpenAI, Anthropic, Gemini e Ollama. Chaves opcionais ficam no arquivo privado `~/.local/share/my-dev-environment/.env`.

## Reconfigurar

Execute novamente o instalador e depois `devbox restart` no diretório do projeto para reconstruir a imagem com o novo perfil.

Nunca compartilhe o arquivo local de credenciais.
