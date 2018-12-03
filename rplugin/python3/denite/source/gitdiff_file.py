import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from _gitdiff_base import GitDiffBase

finally:
    sys.path.remove(os.path.dirname(__file__))


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
        self.name = 'gitdiff_file'
        self.kind = 'gitdiff_file'

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
