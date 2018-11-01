import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from gitdiff_base import GitBase

finally:
    sys.path.remove(os.path.dirname(__file__))


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
            '--sort=-committerdate',
            '--format=%(HEAD) %(refname:short)',
            'refs/heads',
            'refs/remotes',
        ]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self.run_command(self._cmd)

        candidates = [{
            'word': r,
            'abbr': r,
            'action__branch': r.split()[-1],
            'action__basebranch': self.git_head,
        } for r in res]

        return candidates
