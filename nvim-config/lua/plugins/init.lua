return {
  {
    "nvchad/base46",
    branch = "v3.0",
    build = function()
      require("base46").load_all_highlights()
    end,
  },
  {
    "nvchad/ui",
    branch = "v3.0",
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

  -- GitHub Copilot: run :Copilot auth inside Neovim after the first launch.
  {
    "github/copilot.vim",
    cond = vim.env.ENABLE_COPILOT == "1",
    event = "InsertEnter",
  },

  -- Multi-provider chat/inline assistant: OpenAI, Anthropic, Gemini and Ollama.
  {
    "olimorris/codecompanion.nvim",
    cond = vim.env.ENABLE_CODECOMPANION == "1",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-treesitter/nvim-treesitter",
    },
    opts = {},
    cmd = { "CodeCompanion", "CodeCompanionChat", "CodeCompanionActions" },
    keys = {
      { "<leader>aa", "<cmd>CodeCompanionActions<cr>", mode = { "n", "v" }, desc = "AI actions" },
      { "<leader>ac", "<cmd>CodeCompanionChat Toggle<cr>", mode = { "n", "v" }, desc = "AI chat" },
      { "<leader>ai", "<cmd>CodeCompanion<cr>", mode = { "n", "v" }, desc = "AI inline" },
    },
  },
}
