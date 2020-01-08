import os
from subprocess import PIPE, STDOUT, CalledProcessError, Popen, check_output

from denite import util
from denite.base.source import Base


class GitBase(Base):
    _HIGHLIGHT_SYNTAX = []

    def __init__(self, vim):
        super().__init__(vim)

        self.git_rootpath = ""
        self.git_head = "HEAD"
        self._cmd = []

    def highlight(self):
        for dic in self._HIGHLIGHT_SYNTAX:
            self.vim.command(
                "syntax match {0}_{1} /{2}/ contained containedin={0}".format(
                    self.syntax_name, dic["name"], dic["re"]
                )
            )
            self.vim.command(
                "highlight default link {0}_{1} {2}".format(
                    self.syntax_name, dic["name"], dic["link"]
                )
            )

    def get_git_root(self, cwd, filepath=None):
        if os.path.exists(filepath):
            dirpath = os.path.dirname(filepath)
        else:
            dirpath = cwd
        dirpath = os.path.abspath(dirpath)

        root_path = ""
        while dirpath != "/":
            for dir_ in os.scandir(dirpath):
                if ".git" == dir_.name:
                    root_path = os.path.abspath(dir_)

            dirpath = os.path.dirname(dirpath)

        return root_path

    def on_init(self, context):
        git_rootpath = self.vim.eval('get(b:, "git_dir", "")')
        if not git_rootpath:
            filepath = self.vim.current.buffer.name
            git_rootpath = self.get_git_root(context["path"], filepath)
            self.vim.command(':let b:git_dir = "%s"' % git_rootpath)

        os.chdir(os.path.dirname(git_rootpath))
        self.git_rootpath = os.path.dirname(git_rootpath)

    def run_command(self, cmd):
        try:
            res = check_output(cmd, cwd=self.git_rootpath, stderr=STDOUT).decode(
                "utf-8"
            )

            return [r for r in res.split("\n") if r]
        except CalledProcessError as e:
            util.error(self.vim, e.output.decode("utf-8"))
            return []

    def run_command_gen(self, cmd):
        try:
            proc = Popen(cmd, cwd=self.git_rootpath, stdout=PIPE)
            for line in proc.stdout:
                if line:
                    yield line.decode("utf-8")
        except CalledProcessError as e:
            util.error(self.vim, e.output.decode("utf-8"))
            return []

    def gather_candidates(self, context):
        pass


class GitDiffBase(GitBase):
    def _on_init_diff(self, context):
        super().on_init(context)
        if context["args"] and context["args"][0] != "input":
            target = context["args"][0]
        else:
            target = self.vim.eval('get(g:, "denite_gitdiff_target", "")')

            target_input = self.vim.call(
                "denite#util#input",
                "Target: " if target == "" else "Target [{}]: ".format(target),
                "",
                "custom,DeniteGitDiffCompleteRev",
            )
            target = target_input or target
            self.vim.command('let g:denite_gitdiff_target = "{}"'.format(target))

        base = (context["args"][1:2] or ["HEAD"])[0]
        filter_val = (context["args"][2:3] or [""])[0]
        target_file = (context["args"][3:4] or [""])[0]
        context["__target"] = target
        context["__base"] = base
        context["__filter_val"] = filter_val
        context["__target_file"] = target_file

    def on_init(self, context):
        self._on_init_diff(context)
