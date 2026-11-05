FROM debian:bookworm-slim

ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=1000
ARG EDITOR_CHOICE=nvim
ARG INSTALL_RUST=0
ARG INSTALL_CPP=0
ARG INSTALL_PYTHON=0
ARG INSTALL_NODE=0
ARG INSTALL_GO=0
ARG INSTALL_JAVA=0
ARG NVIM_VERSION=stable

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    SHELL=/bin/zsh

RUN set -eux; \
    packages="ca-certificates curl wget ssh gh git unzip tar gzip xz-utils gnupg sudo locales tmux zsh jq ripgrep fd-find"; \
    if [ "$INSTALL_CPP" = "1" ]; then packages="$packages build-essential gcc g++ gdb valgrind cmake ninja-build pkg-config clang clangd clang-format lld lldb"; fi; \
    if [ "$INSTALL_PYTHON" = "1" ]; then packages="$packages python3 python3-pip python3-venv python3-dev"; fi; \
    if [ "$INSTALL_JAVA" = "1" ]; then packages="$packages openjdk-17-jdk-headless"; fi; \
    if [ "$EDITOR_CHOICE" = "vim" ]; then packages="$packages vim"; fi; \
    if [ "$EDITOR_CHOICE" = "helix" ]; then packages="$packages helix"; fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends $packages; \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen; \
    locale-gen; \
    ln -sf /usr/bin/fdfind /usr/local/bin/fd; \
    rm -rf /var/lib/apt/lists/*

RUN if [ "$INSTALL_NODE" = "1" ]; then \
      curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
      apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*; \
    fi

RUN if [ "$INSTALL_GO" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends golang-go && rm -rf /var/lib/apt/lists/*; \
    fi

RUN if [ "$EDITOR_CHOICE" = "nvim" ]; then \
      ARCH=$(dpkg --print-architecture); \
      if [ "$ARCH" = "arm64" ]; then NVIM_ARCH="arm64"; else NVIM_ARCH="x86_64"; fi; \
      curl -fsSL "https://github.com/neovim/neovim/releases/download/${NVIM_VERSION}/nvim-linux-${NVIM_ARCH}.tar.gz" -o /tmp/nvim.tar.gz; \
      tar -C /opt -xzf /tmp/nvim.tar.gz; \
      ln -sf "/opt/nvim-linux-${NVIM_ARCH}/bin/nvim" /usr/local/bin/nvim; \
      rm /tmp/nvim.tar.gz; \
    fi

RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then LG_ARCH="arm64"; else LG_ARCH="x86_64"; fi && \
    LAZYGIT_VERSION=$(curl -fsSL https://api.github.com/repos/jesseduffield/lazygit/releases/latest | grep -Po '"tag_name": "v\K[^"]*') && \
    curl -fsSL -o /tmp/lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_${LG_ARCH}.tar.gz" && \
    tar -C /tmp -xzf /tmp/lazygit.tar.gz lazygit && install -m 755 /tmp/lazygit /usr/local/bin/lazygit && rm -rf /tmp/lazygit*

RUN curl -fsSL https://starship.rs/install.sh | sh -s -- --yes

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m -s /bin/zsh $USERNAME && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME
ENV RUSTUP_HOME=/home/$USERNAME/.rustup \
    CARGO_HOME=/home/$USERNAME/.cargo \
    PATH="/home/$USERNAME/.cargo/bin:/home/$USERNAME/.local/share/nvim/mason/bin:/home/$USERNAME/.local/bin:${PATH}"

RUN if [ "$INSTALL_RUST" = "1" ]; then \
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable && \
      rustup component add rust-analyzer clippy rustfmt; \
    fi

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions && \
    git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

RUN if [ "$EDITOR_CHOICE" = "nvim" ]; then \
      git clone --depth 1 https://github.com/NvChad/starter /home/$USERNAME/.config/nvim && \
      rm -rf /home/$USERNAME/.config/nvim/.git; \
    fi

COPY --chown=$USERNAME:$USERNAME ./nvim-config/ /home/$USERNAME/.config/nvim/
COPY --chown=$USERNAME:$USERNAME ./.zshrc /home/$USERNAME/.zshrc

RUN if [ "$EDITOR_CHOICE" = "nvim" ]; then nvim --headless "+Lazy! sync" +qa; fi

WORKDIR /workspace
CMD ["sleep", "infinity"]
