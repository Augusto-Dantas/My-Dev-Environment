export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME=""
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
source $ZSH/oh-my-zsh.sh

export EDITOR="${EDITOR:-nvim}"
export VISUAL="$EDITOR"
export PAGER="less"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

if command -v nvim >/dev/null 2>&1; then
  alias v="nvim"
  alias vi="nvim"
  alias vim="nvim"
elif command -v vim >/dev/null 2>&1; then
  alias v="vim"
  alias vi="vim"
elif command -v hx >/dev/null 2>&1; then
  alias v="hx"
  alias vi="hx"
  alias vim="hx"
fi

alias lg="lazygit"
alias ll="ls -lAh --color=auto"
alias gs="git status -sb"
alias gl="git log --oneline --graph --decorate"

eval "$(starship init zsh)"
