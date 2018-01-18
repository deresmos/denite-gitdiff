import concurrent.futures
from copy import deepcopy

from .gitdifflog import Source


def _get_previous_hash(res, hash):
    for x in res:
        if len(x) > 1 and hash == x[0]:
            return x[1]
    else:
        return ''


def _get_descendant_hashes(res, base_hash):
    hash = base_hash
    hashes = [base_hash]
    while True:
        hash = _get_previous_hash(res, hash)
        if hash:
            hashes.append(hash)
        else:
            break
    return hashes


class Source(Source):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiffloghash'
        self.kind = 'gitdifflog'

    def get_hash_merged(self, context):
        cmd = deepcopy(self._cmd)
        cmd += [
            'log',
            '--oneline',
            '--reverse',
            '--ancestry-path',
            '--pretty=format:%h %p',
            '{}..'.format(context['__target'], context['__base']),
        ]
        res = [x.split() for x in self._run_command(cmd)]
        return self._get_hash_merged_branch(res, context['__target'])

    @staticmethod
    def _get_hash_merged_branch(res, commit):
        if not len(res[0]):
            return ''

        hash = commit
        for x in res:
            if not x:
                return ''

            if hash == x[1]:
                hash = x[0]
                continue

            if len(x) == 3 and hash == x[2]:
                return x[0]
        else:
            return ''

    def _get_hash_checkouted(self, context, merged_hash):
        cmd = deepcopy(self._cmd)
        cmd += [
            'log',
            merged_hash,
            '--pretty=format:%H %P',
        ]
        res = [x.split() for x in self._run_command(cmd)]
        return self._get_first_hash_of_branch(res)

    def _get_first_hash_of_branch(self, res):
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
        tasks = []
        tasks += [executor.submit(_get_descendant_hashes, res, res[0][1])]
        tasks += [executor.submit(_get_descendant_hashes, res, res[0][2])]

        tmp = []
        for task in concurrent.futures.as_completed(tasks):
            hashes = task.result()
            tmp += hashes
            if hashes[0] == res[0][2]:
                r = hashes
        base_checkout_hash = [
            e for e in sorted(set(tmp), key=tmp.index) if tmp.count(e) > 1
        ][0]
        return r[r.index(base_checkout_hash) - 1]

    def on_init(self, context):
        self._on_init_diff(context)
        merged_hash = self.get_hash_merged(context)
        context['__base'] = merged_hash
        if merged_hash:
            context['__target'] = self._get_hash_checkouted(
                context, merged_hash)

    def gather_candidates(self, context):
        if not context['__base']:
            return []

        cmd = deepcopy(self._cmd)
        cmd += [
            'log',
            '--ancestry-path',
            '{}..{}'.format(context['__target'], context['__base']),
            '--pretty=format:%h < %p| %cd [%an] %s %d',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        res = []
        res += self._run_command(cmd)

        cmd = deepcopy(self._cmd)
        cmd += [
            'log',
            '--oneline',
            context['__target'],
            '-n',
            '1',
            '--pretty=format:%h < %p| %cd [%an] %s %d',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        res += self._run_command(cmd)

        hash_i = 0
        p_hash_i = 2
        filter_val = context['__filter_val']
        git_path = self.git_path
        candidates = [{
            'word': r,
            'abbr': r,
            'base_revision': r.split()[hash_i],
            'target_revision': r.split()[p_hash_i].replace('|', ''),
            'git_path': git_path,
        } for r in res if filter_val in r]

        return candidates
