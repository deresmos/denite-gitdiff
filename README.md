denite-gitdiff
==
Denite source and kind for git diff


Requirements
--
* [vim-fugitive](https://github.com/tpope/vim-fugitive)


Installation
--
* To install using dein:
  ```
  [[plugins]]
  repo = 'deresmos/denite-gitdiff'
  ```


Usage
--
* `gitdiff_file` Comparing target branch.
  e.g.`Denite gitdiff_file[:target_branch:base_branch:filter_val]`
* `gitdifflog` Comparing target branch log.
  e.g.`Denite gitdifflog[:target_branch:base_branch:filter_val:target_file]`


License
--
Released under the MIT license, see LICENSE.
