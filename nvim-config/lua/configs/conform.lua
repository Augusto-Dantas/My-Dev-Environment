return {
  formatters_by_ft = {
    lua = { "stylua" },
    python = { "ruff_format", "ruff_organize_imports" },
    c = { "clang-format" },
    cpp = { "clang-format" },
    rust = { "rustfmt" },
    javascript = { "prettier" },
    typescript = { "prettier" },
    json = { "prettier" },
    yaml = { "prettier" },
    sh = { "shfmt" },
    bash = { "shfmt" },
  },
  format_on_save = {
    timeout_ms = 1000,
    lsp_fallback = true,
  },
}
