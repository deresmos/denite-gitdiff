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
            're': r'\v\w+ \< (\w+| )+\|'
        },
    ]

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdifflog'
        self.kind = 'gitdifflog'

    def on_init(self, context):
        self._on_init_diff(context)
        cmd = self._cmd
        cmd += [
            'log',
            '--oneline',
            '--pretty=format:%h < %p| %cd [%an] %s',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        target = context['__target']
        if target != '':
            cmd += [target + '...' + context['__base']]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self._run_command(self._cmd)

        hash_i = 0
        p_hash_i = 2
        candidates = [{
            'word': r,
            'abbr': r,
            'hash': r.split()[hash_i],
            'p_hash': r.split()[p_hash_i],
        } for r in res]

        return candidates
