import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from gitdiff_log import Source as GitDiffLogSource

finally:
    sys.path.remove(os.path.dirname(__file__))


def _gen_previous_hash(res, _hash):
    for x in res:
        if len(x) > 1 and _hash == x[0]:
            _hash = x[1]
            yield _hash
    else:
        yield ''


def _gen_descendant_hash(res, base_hash):
    yield base_hash

    get_previous_hash_gen = _gen_previous_hash(res, base_hash)
    for _hash in get_previous_hash_gen:
        if _hash:
            yield _hash
        else:
            break


class Source(GitDiffLogSource):
    EMPTY_HASHES = ('', '')

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiff_branchlog'
        self.kind = 'gitdiff_log'

    def get_hash_merged(self, context):
        cmd = [
            'git',
            'log',
            '--oneline',
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
                return (x[0], x[2])

            if _hash == x[1]:
                _hash = x[0]
                continue

        return self.EMPTY_HASHES

    def _get_hash_checkouted(self, context, merged_hash):
        cmd = ['git', 'log', merged_hash, '--pretty=format:%h %p', '-n', '1']
        res = [x.split() for x in self.run_command(cmd)]

        r = self._gen_descendant_hash(res, res[0][2])
        l = list(self._gen_descendant_hash(res, res[0][1]))

        checkout_hash = None
        for x in r:
            if x in l:
                checkout_hash = x
                break

        return checkout_hash

    def _gen_descendant_hash(self, res, target_hash):
        log_num = self.vim.eval('get(g:, "denite_gitdiff_log_num", 1000)')
        cmd = [
            'git',
            'log',
            '--first-parent',
            '--pretty=format:%h',
            '-n',
            str(log_num),
            target_hash,
        ]
        gen_line = self.run_command_gen(cmd)

        for _hash in gen_line:
            if _hash:
                yield _hash.strip()
            else:
                break

    def on_init(self, context):
        super().on_init(context)
        merged_hash, pre_merged_hash = self.get_hash_merged(context)
        context['__base'] = merged_hash
        if merged_hash:
            context['__target'] = self._get_hash_checkouted(
                context, merged_hash)
            self._pre_merged_hash = pre_merged_hash

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
            '--pretty=format:%h < %p| %cd [%an] %s %d',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        res += self.run_command(cmd)

        cmd = [
            'git',
            'log',
            '--ancestry-path',
            '--first-parent',
            '{}...{}'.format(context['__target'], self._pre_merged_hash),
            '--pretty=format:%h < %p| %cd [%an] %s %d',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        res += self.run_command(cmd)

        hash_i = 0
        p_hash_i = 2
        filter_val = context['__filter_val']
        git_rootpath = self.git_rootpath
        candidates = [{
            'word': r,
            'abbr': r,
            'base_revision': r.split()[hash_i],
            'target_revision': r.split()[p_hash_i].replace('|', ''),
            'git_rootpath': git_rootpath,
        } for r in res if filter_val in r]

        return candidates
