import glob
import itertools
import os
import subprocess

from git import Repo

from denite import util

from .base import Base


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'diffbranch'
        self.kind = 'diffbranch'

    def on_init(self, context):
        if context['args']:
            target = context['args'][0]
        else:
            target = util.input(self.vim, context, 'Target: ')

        target = target or self.vim.eval(
            'get(g:, "denite_gitdiff_target", "")')
        self.vim.command('let g:denite_gitdiff_target = "{}"'.format(target))
        context['__target'] = target
        try:
            git_path = self.vim.eval('fnamemodify(b:git_dir, \':p:h:h\')')
            self.__git = Repo(git_path)
            os.chdir(git_path)
        except:
            pass

    def gather_candidates(self, context):
        try:
            candidates = [{
                'word':
                diff.a_path,
                'abbr':
                '{}: {}'.format(diff.change_type, diff.a_path),
                'action__path':
                os.path.abspath(diff.a_path),
                'target_branch':
                context['__target']
            } for diff in self.__git.index.diff(context['__target'])]

        except:
            candidates = []

        return candidates
