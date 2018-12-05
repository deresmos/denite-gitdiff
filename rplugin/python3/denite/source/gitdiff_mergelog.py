import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from gitdiff_branchlog import Source as BranchLogSource

finally:
    sys.path.remove(os.path.dirname(__file__))


class Source(BranchLogSource):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiff_mergelog'
        self.kind = 'gitdiff_log'

    def get_hash_merged(self, context):
        cmd = [
            'git',
            'log',
            '--oneline',
            '--pretty=format:%h %p',
            '-n',
            '1',
            context['__target'],
        ]
        res = [x.split() for x in self.run_command(cmd)]

        if not res:
            return self.EMPTY_HASHES

        return (res[0][0], res[0][2])
