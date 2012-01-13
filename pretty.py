import sublime, sublime_plugin
import re, os, json
import xml.dom.minidom as minidom

class PrettyPrintXmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		syntax_file_name = self.view.settings().get('syntax')
		extension = syntax_file_name.split('/')[-1].split('.')[0]

		if not extension:
			file_name = self.view.file_name()
			if file_name:
				extension = file_name.split('.')[-1]
		
		if extension:
			extension = extension.lower()

			if extension == 'xml':
				self.prettify_xml(edit)
			elif extension == 'json':
				self.prettify_json(edit)

	def prettify_xml(self, edit):
	  view = self.view
	  for region in view.sel():
		 str_xml = "".join(re.split("\n[ \t]*", view.substr(region)))
		 result = minidom.parseString(str_xml).toprettyxml()

		 self.view.replace(edit, region, str(result))

	def prettify_json(self, edit):
		for region in self.view.sel():
		 str_json = "".join(re.split("\n[ \t]*", self.view.substr(region)))
		 result = json.loads(str_json)

		 self.view.replace(edit, region, str(json.dumps(result, sort_keys=True, indent=4)))