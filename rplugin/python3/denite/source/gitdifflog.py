import os
from subprocess import check_output

from denite import util

from .gitdiffbranch import GitDiffBase


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
            'link': 'Number',
            're': r'\v\w+\|'
        },
    ]

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdifflog'
        self.kind = ''

    def on_init(self, context):
        self._on_init_diff(context)
        cmd = self._cmd
        cmd += [
            'log', '--oneline', '--pretty=format:%h| %cd [%an] %s',
            '--date=format:%Y-%m-%d %H:%M:%S'
        ]
        target = context['__target']
        if target != '':
            cmd += [self.git_head + '...' + target]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self._run_command(self._cmd)
        candidates = [{
            'word': r,
            'abbr': r,
        } for r in res]

        return candidates
