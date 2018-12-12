import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from _gitdiff_base import GitDiffBase

finally:
    sys.path.remove(os.path.dirname(__file__))

_GIT_LOG_BRANCH_SYNTAX = ('syntax match {0}_branch '
                          r'/\v\|\s+\(.+\)/ '
                          'contained containedin={0}')

_GIT_LOG_L_BRANCH_SYNTAX = ('syntax match {0}_lBranch '
                            r'/\v(\w|\/)+/ '
                            'contained containedin={0}_branch')
_GIT_LOG_L_BRANCH_HIGHLIGHT = 'highlight default link {0}_lBranch Number'


class Source(GitDiffBase):
    _HIGHLIGHT_SYNTAX = [
        {
            'name': 'gitLogAuthor',
            'link': 'Function',
            're': r'\v\[.+\]'
        },
        {
            'name': 'gitLogDate',
            'link': 'Comment',
            're': r'\v\d{4}-\d{1,2}-\d{1,2}[ \t]\d{1,2}:\d{1,2}:\d{1,2}'
        },
        {
            'name': 'gitLogHash',
            'link': 'Comment',
            're': r'\v\zs\w+\ze\|'
        },
        {
            'name': 'gitLogSeparator',
            'link': 'Tag',
            're': r'\v\|'
        },
    ]
    FORMAT = [
        '--pretty=format:%h| %s | %d [%an] %cd < %p < %H %P',
        '--date=format:%Y-%m-%d %H:%M:%S',
    ]

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiff_log'
        self.kind = 'gitdiff_log'
        self.sorters = []

    def highlight(self):
        super().highlight()
        self.vim.command(_GIT_LOG_BRANCH_SYNTAX.format(self.syntax_name))
        self.vim.command(_GIT_LOG_L_BRANCH_SYNTAX.format(self.syntax_name))
        self.vim.command(_GIT_LOG_L_BRANCH_HIGHLIGHT.format(self.syntax_name))

    def on_init(self, context):
        super().on_init(context)
        cmd = [
            'git',
            'log',
            '--oneline',
        ]
        cmd += self.FORMAT

        target = context['__target']
        base = context['__base']
        if target and base:
            cmd += [target + '..' + base]
        elif target:
            cmd += [target]

        if context['__target_file']:
            cmd += [context['__target_file']]
        self._cmd = cmd

    def gather_candidates(self, context):
        lines = self.run_command_gen(self._cmd)

        filter_val = context['__filter_val']
        _candidates = self._gather_candidates
        candidates = [
            _candidates(context, line) for line in lines if filter_val in line
        ]

        return candidates

    def _gather_candidates(self, context, line):
        hash_i = 0
        target_file = context['__target_file']

        candidates = {
            'word': line,
            'abbr': line.split(' <')[0],
            'base_revision': line.split('|')[hash_i],
            'git_rootpath': self.git_rootpath,
            'target_file': target_file,
        }

        target = line.split(' <')[1].split()[0:1]
        if target:
            candidates['target_revision'] = target[0]
        else:
            candidates['target_revision'] = ''

        return candidates
