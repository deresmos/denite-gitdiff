import os
import sys

from denite import util
from denite.kind.file import Kind as KindFile

try:
    sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))
    from _gitdiff_base import GitBase

finally:
    sys.path.remove(os.path.join(os.path.dirname(__file__), '..'))


class Kind(KindFile):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitbranch'
        self.default_action = 'checkout'

        self._base = GitBase(vim)

    def init_run(self, context):
        self._base.on_init(context)

    def action_checkout(self, context):
        self.init_run(context)
        target = context['targets'][0]
        t_branch = target['action__branch']
        cmd = ['git', 'checkout', t_branch]
        self._base.run_command(cmd)

    def action_delete(self, context):
        self.init_run(context)
        for target in context['targets']:
            t_branch = target['action__branch']
            cmd = ['git', 'branch', '-d', t_branch]
            self._base.run_command(cmd)

    def action_delete_force(self, context):
        self.init_run(context)
        for target in context['targets']:
            t_branch = target['action__branch']
            msg = 'Force delete {}? [y/n] : '.format(t_branch)
            force = util.input(self.vim, context, msg) == 'y'
            if force:
                cmd = ['git', 'branch', '-D', t_branch]
                self._base.run_command(cmd)

    def action_diffbranchlog(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdifflog',
                'args': [ctx['action__branch'], ctx['action__basebranch']]
            },
        ])

    def action_diffbranch(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdiffbranch',
                'args': [ctx['action__branch'], ctx['action__basebranch']]
            },
        ])

    def action_branchlog(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdifflog',
                'args': [ctx['action__branch'], '']
            },
        ])
