import os
from subprocess import STDOUT, CalledProcessError, check_output

from denite import util

from .base import Base


class GitBase(Base):
    _HIGHLIGHT_SYNTAX = []

    def __init__(self, vim):
        super().__init__(vim)

        self.git_rootpath = ''
        self.git_head = ''
        self._cmd = []

    def highlight(self):
        for dic in self._HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, dic['name'], dic['re']))
            self.vim.command('highlight default link {0}_{1} {2}'.format(
                self.syntax_name, dic['name'], dic['link']))

    def on_init(self, context):
        git_rootpath = self.vim.eval('b:git_dir')
        self.git_rootpath = os.path.dirname(git_rootpath)
        os.chdir(self.git_rootpath)

        head = self.vim.eval('fugitive#head()')
        self.git_head = head

    def run_command(self, cmd):
        try:
            res = check_output(
                cmd, cwd=self.git_rootpath, stderr=STDOUT).decode('utf-8')

            return [r for r in res.split('\n') if r]
        except CalledProcessError as e:
            util.error(self.vim, e.output.decode('utf-8'))
            return []


class GitDiffBase(GitBase):
    def _on_init_diff(self, context):
        super().on_init(context)
        if context['args'] and context['args'][0] != 'input':
            target = context['args'][0]
        else:
            target = self.vim.eval('get(g:, "denite_gitdiff_target", "")')

            target_input = util.input(
                self.vim,
                context,
                'Target: ' if target == '' else 'Target [{}]: '.format(target),
                completion='custom,DeniteGitDiffCompleteRev')
            target = target_input or target
            self.vim.command(
                'let g:denite_gitdiff_target = "{}"'.format(target))

        base = (context['args'][1:2] or ['HEAD'])[0]
        filter_val = (context['args'][2:3] or [''])[0]
        target_file = (context['args'][3:4] or [''])[0]
        context['__target'] = target
        context['__base'] = base
        context['__filter_val'] = filter_val
        context['__target_file'] = target_file

    def on_init(self, context):
        self._on_init_diff(context)


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
        super().on_init(context)
        cmd = ['git', 'diff', '--name-status']

        target = context['__target']
        base = context['__base']
        if target and base:
            cmd += [target + '...' + base]
        elif target:
            cmd += [target]
        elif base:
            cmd += [base]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self.run_command(self._cmd)
        res = [r.split('\t') for r in res]

        type_i = 0
        path_i = 1
        filter_val = context['__filter_val']
        candidates = [{
            'word': r[path_i],
            'abbr': '{}: {}'.format(r[type_i], r[path_i]),
            'action__path': os.path.abspath(r[path_i]),
            'target_revision': context['__target'],
            'base_revision': context['__base'],
        } for r in res if filter_val in r[type_i] + ' ' + r[path_i]]

        return candidates
