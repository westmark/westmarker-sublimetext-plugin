import sublime_plugin
import re
import json
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
      elif extension == 'js' or extension == 'javascript':
        self.prettify_json(edit)
      elif extension == 'py' or extension == 'python':
        self.prettify_python(edit)

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

  def prettify_python(self, edit):
    OPERATORS = r'\-/\*\+'
    op_str = r'([a-z0-9][{0}][a-z0-9]|[\)\]][{0}][a-z0-9]|[\)\]][{0}][\(\[])'.format(OPERATORS)
    cp_str = r',(?:[^\s])'

    for region in self.view.sel():
      if region.empty():
        crowded_commas = self.view.find_all(cp_str)
        crowded_commas.reverse()

        edit = self.view.begin_edit('PrettyPrintXmlCommand')

        for r in crowded_commas:
          self.view.insert(edit, r.a + 1, ' ')

        crowded_operators = self.view.find_all(op_str)
        crowded_operators.reverse()

        for r in crowded_operators:
          self.view.insert(edit, r.b - 1, ' ')
          self.view.insert(edit, r.a + 1, ' ')

        self.view.end_edit(edit)

      else:
        result = self.view.find(cp_str, region.a)
        while result.a < region.b:
          self.view.insert(edit, result.a + 1, ' ')
          result = self.view.find(cp_str, result.b)

