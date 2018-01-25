from .gitdiffbranch import GitDiffBase

_GIT_LOG_BRANCH_SYNTAX = ('syntax match {0}_branch '
                          r'/\v\(.+\)/ '
                          'contained containedin={0}')

_GIT_LOG_L_BRANCH_SYNTAX = ('syntax match {0}_lBranch '
                            r'/\v(\w|\/)+/ '
                            'contained containedin={0}_branch')
_GIT_LOG_L_BRANCH_HIGHLIGHT = 'highlight default link {0}_lBranch Number'

_GIT_LOG_R_BRANCH_SYNTAX = ('syntax match {0}_rBranch '
                            r'/\v(origin)\/(\w|\/)+/ '
                            'contained containedin={0}_branch')
_GIT_LOG_R_BRANCH_HIGHLIGHT = 'highlight default link {0}_rBranch Function'


class Source(GitDiffBase):
    _HIGHLIGHT_SYNTAX = [
        {
            'name': 'gitLogAuthor',
            'link': 'Function',
            're': r'\v\[.+\]'
        },
        {
            'name': 'gitLogDate',
            'link': 'Comment',
            're': r'\v\d{4}-\d{1,2}-\d{1,2}[ \t]\d{1,2}:\d{1,2}:\d{1,2}'
        },
        {
            'name': 'gitLogHash',
            'link': 'Number',
            're': r'\v\w+ \< (\w+| )+\|'
        },
    ]

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'gitdifflog'
        self.kind = 'gitdifflog'

    def highlight(self):
        super().highlight()
        self.vim.command(_GIT_LOG_BRANCH_SYNTAX.format(self.syntax_name))
        self.vim.command(_GIT_LOG_L_BRANCH_SYNTAX.format(self.syntax_name))
        self.vim.command(_GIT_LOG_L_BRANCH_HIGHLIGHT.format(self.syntax_name))
        self.vim.command(_GIT_LOG_R_BRANCH_SYNTAX.format(self.syntax_name))
        self.vim.command(_GIT_LOG_R_BRANCH_HIGHLIGHT.format(self.syntax_name))

    def on_init(self, context):
        self._on_init_diff(context)
        cmd = self._cmd
        cmd += [
            'log',
            '--oneline',
            '--pretty=format:%h < %p| %cd [%an] %s %d',
            '--date=format:%Y-%m-%d %H:%M:%S',
        ]
        target = context['__target']
        if target != '':
            cmd += [target + '...' + context['__base']]
        if context['__target_file']:
            cmd += [context['__target_file']]
        self._cmd = cmd

    def gather_candidates(self, context):
        res = self._run_command(self._cmd)

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
