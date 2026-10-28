export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME=""
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
source $ZSH/oh-my-zsh.sh

export EDITOR="nvim"
export VISUAL="nvim"
export PAGER="less"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

alias v="nvim"
alias vi="nvim"
alias vim="nvim"

alias lg="lazygit"
alias ll="ls -lAh --color=auto"
alias gs="git status -sb"
alias gl="git log --oneline --graph --decorate"

eval "$(starship init zsh)"
