import os

from .gitdiffbranch import GitBase


class Source(GitBase):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitbranch'
        self.kind = 'gitbranch'

    def on_init(self, context):
        super().on_init(context)
        cmd = [
            'git',
            'for-each-ref',
            '--sort=committerdate',
            '--format=%(refname:short)',
            'refs/heads',
            'refs/remotes',
        ]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self.run_command(self._cmd)

        candidates = [{
            'word': r,
            'abbr': r,
            'action__path': os.path.abspath(r),
        } for r in res]

        return candidates
