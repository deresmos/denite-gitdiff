from itertools import filterfalse

from .base import Base, _yank


class Kind(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdifflog'
        self.default_action = 'open'
        self._previewed_target = {}

    def action_open(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdiffbranch',
                'args': [ctx['target_revision'], ctx['base_revision']]
            },
        ])

    def action_gedit(self, context):
        ctx = context['targets'][0]
        self.vim.command('Gedit {}:%'.format(ctx['base_revision']))

    def action_tabgedit(self, context):
        ctx = context['targets'][0]
        self.vim.command('tab split | :Gedit {}:%'.format(
            ctx['base_revision']))

    def action_openvdiff(self, context):
        ctx = context['targets'][0]
        self.vim.command('Gedit {}:% | :Gvdiff {}'.format(
            ctx['base_revision'],
            ctx['target_revision'],
        ))

    def action_openvdiff_local(self, context):
        ctx = context['targets'][0]
        self.vim.command('Gvdiff {}'.format(ctx['target_revision']))

    def action_tabvdiff(self, context):
        ctx = context['targets'][0]
        self.vim.command('tab split | :Gedit {}:% | :Gvdiff {}'.format(
            ctx['base_revision'],
            ctx['target_revision'],
        ))

    def action_tabvdiff_local(self, context):
        ctx = context['targets'][0]
        self.vim.command('tab split | :Gvdiff {}'.format(
            ctx['target_revision'], ))

    def action_yank(self, context):
        _yank(self.vim,
              "\n".join([x['base_revision'] for x in context['targets']]))

    def action_yank_p_hash(self, context):
        _yank(self.vim,
              "\n".join([x['target_revision'] for x in context['targets']]))

    def action_branch_log(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdiffloghash',
                'args': [ctx['target_revision']]
            },
        ])

    def action_preview(self, context):
        target = context['targets'][0]
        tmp_op = self.vim.options['splitbelow']
        self.vim.options['splitbelow'] = False

        if (not context['auto_preview'] and self.__get_preview_window()
                and self._previewed_target == target):
            self.vim.command('pclose!')
            return

        prev_id = self.vim.call('win_getid')
        self.vim.command('pedit! denite_gitdiff_preview')
        self.vim.command('wincmd P')
        self.vim.command('lcd {}'.format(target['git_rootpath']))
        self.vim.command('setlocal filetype=agit_stat')
        self.vim.command(
            'setlocal nobuflisted buftype=nofile bufhidden=unload')
        self.vim.command('read! git show --stat {}'.format(
            target['base_revision']))
        self.vim.command('1,1delete')
        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target
        self.vim.options['splitbelow'] = tmp_op

    def __get_preview_window(self):
        return next(
            filterfalse(lambda x: not x.options['previewwindow'],
                        self.vim.windows), None)
