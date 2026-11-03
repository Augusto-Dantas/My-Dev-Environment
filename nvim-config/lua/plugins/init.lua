return {
  {
    "nvchad/base46",
    branch = "v2.5",
    build = function()
      require("base46").load_all_highlights()
    end,
  },
  {
    "nvchad/ui",
  },
  {
    "stevearc/conform.nvim",
    event = "BufWritePre",
    opts = require("configs.conform"),
  },
  {
    "neovim/nvim-lspconfig",
    config = function()
      require("configs.lspconfig")
    end,
  },
  {
    "nvim-treesitter/nvim-treesitter",
    opts = {
      ensure_installed = {
        "c", "cpp", "cmake", "make", "rust", "ron",
        "python", "julia", "lua", "vim", "vimdoc",
        "javascript", "typescript", "json", "yaml", "toml",
        "bash", "dockerfile", "markdown", "markdown_inline",
      },
      highlight = { enable = true },
      indent = { enable = true },
    },
  },
  {
    "kdheepak/lazygit.nvim",
    cmd = { "LazyGit", "LazyGitConfig", "LazyGitCurrentFile" },
    dependencies = { "nvim-lua/plenary.nvim" },
  },
}
