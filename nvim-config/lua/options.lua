require("nvchad.options")

local o = vim.o
local opt = vim.opt

o.cursorlineopt = "both"
o.relativenumber = true
o.scrolloff = 8
o.sidescrolloff = 8
o.shiftwidth = 8
o.tabstop = 8
o.expandtab = true

vim.g.clipboard = {
  name = "OSC 52",
  copy = {
    ["+"] = require("vim.ui.clipboard.osc52").copy("+"),
    ["*"] = require("vim.ui.clipboard.osc52").copy("*"),
  },
  paste = {
    ["+"] = require("vim.ui.clipboard.osc52").paste("+"),
    ["*"] = require("vim.ui.clipboard.osc52").paste("*"),
  },
}
opt.clipboard = "unnamedplus"
