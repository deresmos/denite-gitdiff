import os

from git import Repo

from denite import util

from .base import Base


class GitDiffBase(Base):
    _HIGHLIGHT_SYNTAX = []

    def __init(self, vim):
        super().__init__(vim)

        self.git_path = ''
        self.git_head = ''
        self._cmd = []

    def highlight(self):
        for dic in self._HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, dic['name'], dic['re']))
            self.vim.command('highlight default link {0}_{1} {2}'.format(
                self.syntax_name, dic['name'], dic['link']))

    def _on_init_diff(self, context):
        if context['args']:
            target = context['args'][0]
        else:
            target = util.input(self.vim, context, 'Target: ')

        target = target or self.vim.eval(
            'get(g:, "denite_gitdiff_target", "")')
        self.vim.command('let g:denite_gitdiff_target = "{}"'.format(target))
        context['__target'] = target

        try:
            git_path = self.vim.eval('b:git_dir')
            head = self.vim.eval('fugitive#head()')

            cmd = ['git', '--git-dir={}'.format(git_path)]

            self._cmd = cmd
            self.git_path = git_path
            self.git_head = head

        except Exception as e:
            raise e


class Source(GitDiffBase):
    _HIGHLIGHT_SYNTAX = [
        {
            'name': 'gitDiffAdd',
            'link': 'DiffAdd',
            're': r'A:'
        },
        {
            'name': 'gitDiffModify',
            'link': 'DiffChange',
            're': r'M:'
        },
        {
            'name': 'gitDiffDelete',
            'link': 'DiffDelete',
            're': r'D:'
        },
    ]

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiffbranch'
        self.kind = 'gitdiffbranch'

    def on_init(self, context):
        try:
            self._on_init_diff(context)
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

        except Exception as e:
            raise e

        return candidates
