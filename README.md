# My-Dev-Environment

Container de desenvolvimento configurável com Docker, Zsh, pacotes por linguagem, editor selecionável e integrações opcionais de IA.

## Instalação sem clonar o repositório completo

Requisitos no host: Docker Engine/Desktop com Compose v2, Git, curl e Python 3.

Baixe e execute somente o instalador:

```bash
curl -fsSL https://raw.githubusercontent.com/Augusto-Dantas/My-Dev-Environment/main/setup.sh | bash
```

O instalador abre uma TUI para escolher:
- Pacotes de linguagem: Rust, C/C++, Python, Node.js/TypeScript, Go e Java.
- Editor: Neovim + NvChad, Vim, Helix ou nenhum.
- Integrações opcionais: GitHub Copilot e CodeCompanion (OpenAI, Anthropic, Gemini ou Ollama).

Por baixo, o instalador faz um *sparse checkout* apenas de `Dockerfile`, `docker-compose.yml`, `.zshrc` e `nvim-config/`. Não baixa o histórico nem o conteúdo desnecessário do repositório. A imagem Docker é construída sob demanda na primeira execução.

## Usar o container em qualquer diretório

Depois da instalação, adicione `~/.local/bin` ao PATH (o instalador informa o comando caso necessário). Acesse qualquer pasta de projeto no host e execute:

```bash
cd ~/projetos/meu-projeto
devbox
```

O diretório atual é montado em `/workspace` dentro do container. Cada diretório do host recebe um ambiente Compose próprio, então você pode abrir projetos diferentes sem trocar manualmente o diretório de instalação.

Comandos:
- `devbox` ou `devbox shell`: iniciar e entrar no ambiente.
- `devbox up`: iniciar em segundo plano.
- `devbox status`: ver o estado.
- `devbox logs`: acompanhar logs.
- `devbox down`: parar/remover o container daquele diretório.
- `devbox restart`: reconstruir e reiniciar.

## Rust

Ao selecionar Rust, a imagem instala rustup com toolchain stable, Cargo, rust-analyzer, Clippy e rustfmt. O cache do Cargo é persistido entre execuções.

## Editores e IA

Copilot e CodeCompanion são habilitados apenas quando Neovim for selecionado. No primeiro uso do Copilot, rode `:Copilot auth`. As chaves de provedores de IA são opcionais e ficam em `~/.local/share/my-dev-environment/.env`, com permissão restrita; nunca são adicionadas ao repositório.

## Reconfigurar

Execute novamente o instalador para selecionar outro conjunto de pacotes/editor. A imagem será reconstruída quando executar `devbox restart` ou `devbox` após atualização da configuração.

## Segurança

Não compartilhe o arquivo local `.env`. Revogue imediatamente qualquer chave que tenha sido exposta.
