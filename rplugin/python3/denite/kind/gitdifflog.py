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
                'args': [ctx['hash'], ctx['p_hash']]
            },
        ])

    def action_yank(self, context):
        _yank(self.vim, "\n".join([x['hash'] for x in context['targets']]))

    def action_yank_p_hash(self, context):
        _yank(self.vim, "\n".join([x['p_hash'] for x in context['targets']]))
