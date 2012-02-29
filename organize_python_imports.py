import ast
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
        code = '\n'.join([self.view.substr(line) for line in self.view.lines(sublime.Region(0, self.view.size()))])

        st = ast.parse(code)
        current_group = None

        for stmt in st.body:
            if stmt.__class__ in [ast.Import, ast.ImportFrom]:
                line_region = self.view.full_line(self.view.text_point(stmt.lineno - 1, 0))
                if not current_group:
                    current_group = ImportGroup(line_region.a, line_region.b)
                    import_groups.append(current_group)
                current_group.imports.append(stmt)
                current_group.end = line_region.b

            else:
                current_group = None

        edit = self.view.begin_edit('OrganizePythonImportsCommand')

        for g in import_groups[-1::-1]:
            imports, from_imports = set(), {}
            for imp in g.imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        if alias.asname:
                            imports.add('import {0} as {1}'.format(alias.name, alias.asname))
                        else:
                            imports.add('import {0}'.format(alias.name))
                else:
                    from_imports.setdefault(imp.module, set())
                    for alias in imp.names:
                        if alias.asname:
                            from_imports[imp.module].add('{0} as {1}'.format(alias.name, alias.asname))
                        else:
                            from_imports[imp.module].add('{0}'.format(alias.name))

            import_str = '\n'.join(sorted(imports)) + '\n'
            import_str += '\n'.join(['from {0} import {1}'.format(p, ', '.join(sorted(from_imports.get(p)))) for p in sorted(from_imports.keys())])

            self.view.replace(edit, sublime.Region(g.start, g.end), import_str.strip('\n') + '\n')

        self.view.end_edit(edit)
