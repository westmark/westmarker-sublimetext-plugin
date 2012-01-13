import sublime, sublime_plugin

class DeleteLineCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			line = self.view.full_line(region)
			self.view.erase(edit, line)