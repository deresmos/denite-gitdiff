from copy import copy

from denite.kind.file import Kind as KindFile


class Kind(KindFile):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdiffbranch'
        self.default_action = 'open'

    def _run_gvdiff(self, context, func, *, local=False):
        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            func(new_context)
            if not local:
                self.vim.command('Gedit {}:%'.format(target['base_revision']))
            self.vim.command('Gvdiff {}'.format(target['target_revision']))

    def action_openvdiff(self, context):
        self._run_gvdiff(context, self.action_open)

    def action_openvdiff_local(self, context):
        self._run_gvdiff(context, self.action_open, local=True)

    def action_tabvdiff(self, context):
        self._run_gvdiff(context, self.action_tabopen)

    def action_tabvdiff_local(self, context):
        self._run_gvdiff(context, self.action_tabopen, local=True)

    def _run_gedit(self, context, func):
        for target in context['targets']:
            new_context = copy(context)
            new_context['targets'] = [target]

            func(new_context)
            self.vim.command('Gedit {}:%'.format(target['base_revision']))

    def action_gedit(self, context):
        self._run_gedit(context, self.action_open)

    def action_tabgedit(self, context):
        self._run_gedit(context, self.action_tabopen)
