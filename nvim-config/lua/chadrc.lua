---@type ChadrcConfig
local M = {}

M.base46 = {
  theme = "onedark",
  transparency = false,
}

M.ui = {
  statusline = { theme = "" },
  tabufline = { enabled = true },
}

M.mason = {
  pkgs = {
    "clangd",
    "clang-format",
    "codelldb",
    "rust-analyzer",
    "lua-language-server",
    "stylua",
    "pyright",
    "ruff",
    "typescript-language-server",
    "bash-language-server",
    "shellcheck",
    "shfmt",
    "dockerfile-language-server",
  },
}

return M
