import os
from subprocess import check_output

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

    @staticmethod
    def _run_command(cmd):
        return check_output(cmd).decode('utf-8').split('\n')[0:-1]


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
        self._on_init_diff(context)
        cmd = self._cmd
        cmd += [
            'diff', '--name-status', self.git_head, context['__target']
        ]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self._run_command(self._cmd)
        res = [r.split('\t') for r in res]

        type_i = 0
        path_i = 1
        candidates = [{
            'word': r[path_i],
            'abbr': '{}: {}'.format(r[type_i], r[path_i]),
            'action__path': os.path.abspath(r[path_i]),
            'target_branch': context['__target'],
        } for r in res]

        return candidates
