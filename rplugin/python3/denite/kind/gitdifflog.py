from itertools import filterfalse

from .base import Base, _yank


class Kind(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdifflog'
        self.default_action = 'open'

    def action_open(self, context):
        ctx = context['targets'][0]
        context['sources_queue'].append([
            {
                'name': 'gitdiffbranch',
                'args': [ctx['target_revision'], ctx['base_revision']]
            },
        ])

    def action_yank(self, context):
        _yank(self.vim,
              "\n".join([x['base_revision'] for x in context['targets']]))

    def action_yank_p_hash(self, context):
        _yank(self.vim,
              "\n".join([x['target_revision'] for x in context['targets']]))

    def action_preview(self, context):
        target = context['targets'][0]

        if (not context['auto_preview'] and self.__get_preview_window()
                and self._previewed_target == target):
            self.vim.command('pclose!')
            return

        prev_id = self.vim.call('win_getid')
        self.vim.command('pedit! denite_gitdiff_preview')
        self.vim.command('wincmd P')
        self.vim.command('lcd {}'.format(target['git_path']))
        self.vim.command('setlocal filetype=agit_stat')
        self.vim.command(
            'setlocal nobuflisted buftype=nofile bufhidden=unload')
        self.vim.command('read! git show --stat {}'.format(
            target['base_revision']))
        self.vim.command('1,1delete')
        self.vim.call('win_gotoid', prev_id)
        self._previewed_target = target

    def __get_preview_window(self):
        return next(
            filterfalse(lambda x: not x.options['previewwindow'],
                        self.vim.windows), None)
