import _ast
import ast
import pyflakes.checker as pyflakes
import sublime
import sublime_plugin


class ImportGroup(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.imports = []


class OrganizePythonImportsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        import_groups = []
        code_lines = []
        line_offset = 0
        filename = sublime.Window.active_view(sublime.active_window()).file_name()

        for line in self.view.lines(sublime.Region(0, self.view.size())):
            line = self.view.substr(line)
            if not line.strip().startswith('# -*- '):
                code_lines.append(line)
            else:
                line_offset += 1

        code = '\n'.join(code_lines)

        try:
            tree = compile(code, filename, 'exec', _ast.PyCF_ONLY_AST)
        except:
            tree = None
        else:
            unused_imports = set()
            for error in pyflakes.Checker(tree, filename).messages:
                if isinstance(error, pyflakes.messages.UnusedImport):
                    unused_imports.add(error.name)

            st = ast.parse(code)
            current_group = None

            for stmt in st.body:
                if stmt.__class__ in [ast.Import, ast.ImportFrom]:
                    line_region = self.view.full_line(self.view.text_point(stmt.lineno - 1 + line_offset, 0))
                    if not current_group:
                        current_group = ImportGroup(line_region.a, line_region.b)
                        import_groups.append(current_group)
                    current_group.imports.append(stmt)
                    current_group.end = max(line_region.b, current_group.end)

                else:
                    current_group = None

            edit = self.view.begin_edit('OrganizePythonImportsCommand')

            for g in import_groups[-1::-1]:
                imports, from_imports = set(), {}
                for imp in g.imports:
                    if isinstance(imp, ast.Import):
                        for alias in imp.names:
                            if alias.asname:
                                if alias.asname not in unused_imports:
                                    imports.add('import {0} as {1}'.format(alias.name, alias.asname))
                            elif alias.name not in unused_imports:
                                imports.add('import {0}'.format(alias.name))
                    else:
                        from_imports.setdefault(imp.module, set())
                        for alias in imp.names:
                            if alias.asname:
                                if alias.asname not in unused_imports:
                                    from_imports[imp.module].add('{0} as {1}'.format(alias.name, alias.asname))
                            elif alias.name not in unused_imports:
                                from_imports[imp.module].add('{0}'.format(alias.name))

                import_str = '\n'.join(sorted(imports)) + '\n'
                for p in sorted(from_imports.keys()):
                    v = from_imports[p]
                    if v:
                        import_str += 'from {0} import {1}'.format(p, ', '.join(sorted(v))) + '\n'

                self.view.replace(edit, sublime.Region(g.start, g.end), import_str.strip('\n') + '\n')

            self.view.end_edit(edit)
