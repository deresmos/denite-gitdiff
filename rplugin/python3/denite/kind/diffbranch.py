from copy import copy

from .file import Kind


class Kind(Kind):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'diffbranch'
        self.default_action = 'open'

    def _run_gvdiff(self, context, func):
        for target in context['targets']:
            branch = target['target_branch']
            new_context = copy(context)
            new_context['targets'] = [target]

            func(new_context)
            self.vim.command('Gvdiff {}'.format(branch))

    def action_openvdiff(self, context):
        self._run_gvdiff(context, self.action_open)

    def action_tabvdiff(self, context):
        self._run_gvdiff(context, self.action_tabopen)
