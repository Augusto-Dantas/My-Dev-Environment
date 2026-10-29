FROM debian:bookworm-slim

ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG NVIM_VERSION=stable

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    EDITOR=nvim \
    SHELL=/bin/zsh

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget ssh gh git unzip tar gzip xz-utils gnupg sudo locales \
    tmux zsh jq ripgrep fd-find \
    build-essential gcc g++ gdb valgrind cmake ninja-build pkg-config \
    clang clangd clang-format lld lldb \
    python3 python3-pip python3-venv python3-dev \
    libssl-dev zlib1g-dev libffi-dev \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then NVIM_ARCH="arm64"; else NVIM_ARCH="x86_64"; fi && \
    curl -fsSL "https://github.com/neovim/neovim/releases/download/${NVIM_VERSION}/nvim-linux-${NVIM_ARCH}.tar.gz" -o /tmp/nvim.tar.gz && \
    tar -C /opt -xzf /tmp/nvim.tar.gz && \
    ln -sf "/opt/nvim-linux-${NVIM_ARCH}/bin/nvim" /usr/local/bin/nvim && \
    rm /tmp/nvim.tar.gz

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then LG_ARCH="arm64"; else LG_ARCH="x86_64"; fi && \
    LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*') && \
    curl -Lo /tmp/lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_${LG_ARCH}.tar.gz" && \
    tar -C /tmp -xzf /tmp/lazygit.tar.gz lazygit && \
    install -m 755 /tmp/lazygit /usr/local/bin/lazygit && \
    rm -rf /tmp/lazygit*

RUN curl -fsSL https://starship.rs/install.sh | sh -s -- --yes

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/zsh $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

ENV RUSTUP_HOME=/home/$USERNAME/.rustup \
    CARGO_HOME=/home/$USERNAME/.cargo \
    PATH="/home/$USERNAME/.cargo/bin:/home/$USERNAME/.local/share/nvim/mason/bin:/home/$USERNAME/.local/bin:${PATH}"

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable \
    && rustup component add rust-analyzer clippy rustfmt

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions \
    && git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

RUN git clone --depth 1 https://github.com/NvChad/starter /home/$USERNAME/.config/nvim \
    && rm -rf /home/$USERNAME/.config/nvim/.git

COPY --chown=$USERNAME:$USERNAME ./nvim-config/ /home/$USERNAME/.config/nvim/
COPY --chown=$USERNAME:$USERNAME ./.zshrc /home/$USERNAME/.zshrc

RUN nvim --headless "+Lazy! sync" +qa || true

WORKDIR /workspace
CMD ["sleep", "infinity"]
