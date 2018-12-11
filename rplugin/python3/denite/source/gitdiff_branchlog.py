import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from gitdiff_log import Source as GitDiffLogSource

finally:
    sys.path.remove(os.path.dirname(__file__))


class Source(GitDiffLogSource):
    EMPTY_HASHES = ('', '', '')

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiff_branchlog'
        self.kind = 'gitdiff_log'

    def get_merged_hash(self, context):
        cmd = [
            'git',
            'log',
            '--reverse',
            '--ancestry-path',
            '--pretty=format:%h %p',
            '{}..{}'.format(context['__target'], context['__base']),
        ]
        gen_line = self.run_command_gen(cmd)
        return self._get_hash_merged_branch(gen_line, context['__target'])

    def _get_hash_merged_branch(self, hashes, commit):
        _hash = commit
        for x in hashes:
            x = x.split()
            if len(x) == 3 and _hash == x[2]:
                return x

            if _hash == x[1]:
                _hash = x[0]
                continue

        return self.EMPTY_HASHES

    def get_merge_base_hash(self, context, left_hash, right_hash):
        cmd = ['git', 'merge-base', left_hash, right_hash]
        merge_base_hash = self.run_command(cmd)
        if merge_base_hash:
            checkout_hash = merge_base_hash[0]
        else:
            checkout_hash = ''

        return checkout_hash

    def on_init(self, context):
        super().on_init(context)
        merged_hash = self.get_merged_hash(context)
        context['__base'] = merged_hash[0]
        if merged_hash != self.EMPTY_HASHES:
            context['__target'] = self.get_merge_base_hash(
                context, merged_hash[1], merged_hash[2])
            self._pre_merged_hash = merged_hash[2]

    def gather_candidates(self, context):
        if not context['__base']:
            return []

        res = []
        cmd = [
            'git',
            'log',
            '--oneline',
            context['__base'],
            '-n',
            '1',
        ]
        cmd += self.FORMAT
        res += self.run_command(cmd)

        cmd = [
            'git',
            'log',
            '--first-parent',
            '{}...{}'.format(context['__target'], self._pre_merged_hash),
        ]
        cmd += self.FORMAT

        res += self.run_command(cmd)

        filter_val = context['__filter_val']
        _candidates = self._gather_candidates
        candidates = [_candidates(context, r) for r in res if filter_val in r]

        return candidates
