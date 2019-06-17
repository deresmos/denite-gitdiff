from itertools import filterfalse
from subprocess import STDOUT, check_output

from denite.base.kind import Base, _yank


class Kind(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = "gitdiff_log"
        self.default_action = "open"
        self.persist_actions += ["preview", "preview_scroll_up", "preview_scroll_down"]
        self._previewed_target = {}

    def action_open(self, context):
        ctx = context["targets"][0]
        context["sources_queue"].append(
            [
                {
                    "name": "gitdiff_file",
                    "args": [ctx["target_revision"], ctx["base_revision"]],
                }
            ]
        )

    def action_gedit(self, context):
        ctx = context["targets"][0]
        self.vim.command("Gedit {}:%".format(ctx["base_revision"]))

    def action_tabgedit(self, context):
        ctx = context["targets"][0]
        self.vim.command("tab split | :Gedit {}:%".format(ctx["base_revision"]))

    def action_openvdiff(self, context):
        ctx = context["targets"][0]
        self.vim.command(
            "Gedit {}:% | :Gvdiff {}".format(
                ctx["base_revision"], ctx["target_revision"]
            )
        )

    def action_openvdiff_local(self, context):
        ctx = context["targets"][0]
        self.vim.command("Gvdiff {}".format(ctx["target_revision"]))

    def action_tabvdiff(self, context):
        ctx = context["targets"][0]
        self.vim.command(
            "tab split | :Gedit {}:% | :Gvdiff {}".format(
                ctx["base_revision"], ctx["target_revision"]
            )
        )

    def action_tabvdiff_local(self, context):
        ctx = context["targets"][0]
        self.vim.command("tab split | :Gvdiff {}".format(ctx["target_revision"]))

    def action_yank(self, context):
        _yank(self.vim, "\n".join([x["base_revision"] for x in context["targets"]]))

    def action_yank_p_hash(self, context):
        _yank(self.vim, "\n".join([x["target_revision"] for x in context["targets"]]))

    def action_branch_log(self, context):
        ctx = context["targets"][0]
        context["sources_queue"].append(
            [{"name": "gitdiff_branchlog", "args": [ctx["base_revision"]]}]
        )

    def action_merge_log(self, context):
        ctx = context["targets"][0]
        context["sources_queue"].append(
            [{"name": "gitdiff_mergelog", "args": [ctx["base_revision"]]}]
        )

    def action_preview_scroll_up(self, context):
        self._preview_scroll(context, "up")

    def action_preview_scroll_down(self, context):
        self._preview_scroll(context, "down")

    def action_reset_soft(self, context):
        self._git_reset("soft", context)

    def action_reset_mixed(self, context):
        self._git_reset("mixed", context)

    def action_reset_hard(self, context):
        self._git_reset("hard", context)

    def action_reset_hard_orig_head(self, context):
        self._git_reset("hard", context, commit_hash="ORIG_HEAD")

    def action_preview(self, context):
        target = context["targets"][0]

        if (
            context["auto_action"] != "preview"
            and self._get_preview_window()
            and self._previewed_target == target
        ):
            self.vim.command("pclose!")
            return
        prev_id = self.vim.call("win_getid")

        self.vim.call("denite#helper#preview_file", context, "diff_log")
        self.vim.command("wincmd P")
        self.vim.command('execute "normal \<C-w>L"')

        self.vim.command("lcd {}".format(target["git_rootpath"]))
        self.vim.command("setlocal filetype=diff")
        self.vim.command("setlocal nobuflisted buftype=nofile bufhidden=unload")
        self.vim.command(
            "silent read! git show --stat {}".format(target["base_revision"])
        )
        self.vim.command(
            "silent read! git diff {}...{}".format(
                target["target_revision"], target["base_revision"]
            )
        )
        self.vim.command("1,1delete")

        self.vim.call("win_gotoid", prev_id)
        self._previewed_target = target

    def _get_preview_window(self):
        return next(
            filterfalse(lambda x: not x.options["previewwindow"], self.vim.windows),
            None,
        )

    def _preview_scroll(self, context, direction):
        prev_id = self.vim.call("win_getid")
        self.vim.command("wincmd P")
        if direction == "up":
            self.vim.command('execute "normal! \<C-u>"')
        elif direction == "down":
            self.vim.command('execute "normal! \<C-d>"')
        self.vim.call("win_gotoid", prev_id)

    def _git_reset(self, mode, context, commit_hash=None):
        target = context["targets"][0]
        commit_hash = commit_hash or target["base_revision"]
        gitroot = target["git_rootpath"]
        args = ["git", "reset", "--" + mode, commit_hash]
        self._run_command(args, gitroot)

    def _run_command(self, cmd, gitroot=""):
        res = check_output(cmd, cwd=gitroot, stderr=STDOUT).decode("utf-8")

        return [r for r in res.split("\n") if r]
