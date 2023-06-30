import ast


class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        self.object_module_mapping: dict[str, str] = {}
        self.imported_modules: set[str] = set()
        self.module_name: str = kwargs["module_name"]

        self.object_name: str = kwargs.get("object_name", "")
        self.defined_objects: dict[str, str] = {}

    def _filter_modules(self, node_module: str) -> bool:
        return False

    def visit_ImportFrom(self, node) -> None:
        if node == None or node.module == None:
            return
        if self._filter_modules(node.module):
            return

        self.imported_modules.add(node.module)
        for node_name in node.names:
            self.object_module_mapping[node_name.name] = node.module

    def visit_FunctionDef(self, node) -> None:
        self.defined_objects[node.name] = node

    def visit_ClassDef(self, node) -> None:
        self.defined_objects[node.name] = node

    def visit_Assign(self, node) -> None:
        for assigned_obj in node.targets:
            curr_value: str = ""
            if "id" not in assigned_obj.__dict__.keys():
                curr_value = assigned_obj.value.id
            else:
                curr_value = assigned_obj.id

            self.defined_objects[curr_value] = node

    def visit_AnnAssign(self, node) -> None:
        curr_value: str = ""
        if "id" not in node.target.__dict__.keys():
            curr_value = node.target.value.id
        else:
            curr_value = node.target.id

        self.defined_objects[curr_value] = node
