function! DeniteGitDiffCompleteRev(A, C, P)
  return fugitive#buffer().repo().git_chomp('rev-parse', '--symbolic', '--branches', '--remotes', '--tags')
endfunction
