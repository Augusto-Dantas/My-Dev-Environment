return {
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
        "bash", "dockerfile", "markdown", "markdown_inline"
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
