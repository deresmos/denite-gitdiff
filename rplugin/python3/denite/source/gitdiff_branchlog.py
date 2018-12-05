import os
import sys

try:
    sys.path.insert(1, os.path.dirname(__file__))
    from gitdiff_log import Source as GitDiffLogSource

finally:
    sys.path.remove(os.path.dirname(__file__))


def _get_previous_hash(res, hash):
    for x in res:
        if len(x) > 1 and hash == x[0]:
            hash = x[1]
            yield hash
    else:
        yield ''


def _get_descendant_hashes(res, base_hash):
    hash = base_hash
    hashes = [base_hash]
    get_previous_hash_gen = _get_previous_hash(res, hash)
    while True:
        hash = next(get_previous_hash_gen)
        if hash:
            hashes.append(hash)
        else:
            get_previous_hash_gen.close()
            break
    return hashes


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
        res = [x.split() for x in self.run_command(cmd)]
        return self._get_hash_merged_branch(res, context['__target'])

    def _get_hash_merged_branch(self, res, commit):
        hash = commit
        for x in res:
            if len(x) == 3 and hash == x[2]:
                return (x[0], x[2])

            if hash == x[1]:
                hash = x[0]
                continue

        else:
            return self.EMPTY_HASHES

    def _get_hash_checkouted(self, context, merged_hash):
        log_num = self.vim.eval('get(g:, "denite_gitdiff_log_num", 1000)')
        cmd = [
            'git',
            'log',
            merged_hash,
            '--pretty=format:%H %P',
            '-n',
            str(log_num),
        ]
        res = [x.split() for x in self.run_command(cmd)]
        return self._get_first_hash_of_branch(res)

    def _get_first_hash_of_branch(self, res):
        l = _get_descendant_hashes(res, res[0][1])
        r = _get_descendant_hashes(res, res[0][2])

        for x in r:
            if x in l:
                base_checkout_hash = x
                break

        return r[r.index(base_checkout_hash)]

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
