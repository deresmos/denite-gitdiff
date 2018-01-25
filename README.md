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
* `gitdiffbranch` Comparing target branch.
  e.g.`Denite gitdiffbranch[:target_branch:base_branch:filter_val]`
* `gitdifflog` Comparing target branch log.
  e.g.`Denite gitdifflog[:target_branch:base_branch:filter_val:target_file]`


License
--
Released under the MIT license, see LICENSE.
