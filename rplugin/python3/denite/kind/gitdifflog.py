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
        _yank(self.vim, "\n".join([x['base_revision'] for x in context['targets']]))

    def action_yank_p_hash(self, context):
        _yank(self.vim, "\n".join([x['target_revision'] for x in context['targets']]))
