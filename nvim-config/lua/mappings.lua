require("nvchad.mappings")

local map = vim.keymap.set

map("n", ";", ":", { desc = "CMD enter command mode" })
map("i", "jk", "<ESC>", { desc = "Escape insert mode" })
map({ "n", "i", "v" }, "<C-s>", "<cmd> w <cr>", { desc = "Save file" })

map("n", "<leader>gg", "<cmd>LazyGit<cr>", { desc = "Open Lazygit" })
map("n", "<leader>gf", "<cmd>LazyGitCurrentFile<cr>", { desc = "Lazygit current file history" })

map("n", "<leader>ca", vim.lsp.buf.code_action, { desc = "LSP Code Action" })
map("n", "<leader>cd", vim.diagnostic.open_float, { desc = "LSP Line Diagnostics" })
map("n", "[d", vim.diagnostic.goto_prev, { desc = "Previous Diagnostic" })
map("n", "]d", vim.diagnostic.goto_next, { desc = "Next Diagnostic" })
map("n", "<leader>ih", function()
  vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled())
end, { desc = "Toggle LSP Inlay Hints" })
