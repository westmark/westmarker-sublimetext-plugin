import re
import sublime
import sublime_plugin


class OrganizePythonImportsCommand(sublime_plugin.TextCommand):

    FROM_RE = re.compile(r'^from\s([^\s]+)\simport ((?:[^\s,]+(?:\sas\s[^,\s]+)?(?:\s*,\s*)?)+)$')
    IMPORT_RE = re.compile(r'^import ((?:[^\s,]+(?:\sas\s[^,\s]+)?(?:\s*,\s*)?)+)$')

    def run(self, edit):
        imports = set()
        from_imports = {}
        header_done = False
        start, end = None, 0

        r = sublime.Region(0, self.view.size())
        for r in self.view.lines(r):
            line = self.view.substr(r)

            fm = self.FROM_RE.match(line)
            im = self.IMPORT_RE.match(line)
            if fm:
                header_done = True
                if start is None:
                    start = r.a
                end = r.b
                for e in [s.strip() for s in fm.group(2).split(',')]:
                    from_imports.setdefault(fm.group(1), set()).add(e)
            elif im:
                header_done = True
                if start is None:
                    start = r.a
                end = r.b
                for e in [s.strip() for s in im.group(1).split(',')]:
                    imports.add(e)
            else:
                if line == '' or (not header_done and line[0].strip() == '#'):
                    continue
                else:
                    break

        import_str = '\n'.join(['import {0}'.format(p) for p in sorted(imports)]) + '\n'
        import_str += '\n'.join(['from {0} import {1}'.format(p, ', '.join(sorted(from_imports.get(p)))) for p in sorted(from_imports.keys())]) + '\n'

        edit = self.view.begin_edit('OrganizePythonImportsCommand')

        self.view.replace(edit, sublime.Region(start, end), import_str.rstrip('\n'))

        self.view.end_edit(edit)
