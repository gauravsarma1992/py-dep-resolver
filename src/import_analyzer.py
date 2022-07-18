import ast
import re
import os
import traceback
from tokenize import tokenize, NAME
from io import BytesIO
from typing import Any


class ModuleHelper:

    @classmethod
    def get_module_name_from_file(cls, file_path: str) -> str:
        module_name: str
        base_dir: str = os.environ.get("BASE_DIR", "")

        file_path = file_path.replace(base_dir, "")
        file_path = file_path.replace(".py", "")
        file_path = file_path.replace("/app/", "")
        split_file_path: list[str] = file_path.split("/")
        if split_file_path[len(split_file_path)-1] == "__init__":
            module_name = ".".join(split_file_path[0:(len(split_file_path)-1)])
        else:
            module_name = ".".join(split_file_path)
        return module_name


    @classmethod
    def get_module_file_from_name(cls, object_name: str, module_name: str) -> str:
        ease_dir: str = os.environ.get("BASE_DIR", "")

        # Check directly in the file by splitting with "."
        generated_path: str = f"{base_dir}/app/{'/'.join(module_name.split('.'))}.py"
        module_path: str = ""
        if os.path.isfile(generated_path):
            return generated_path

        # Check if the __init__ file has imported the elements
        generated_path = f"{base_dir}/app/{'/'.join(module_name.split('.'))}/__init__.py"
        file_visitor = FileVisitor(file_path=generated_path)
        if object_name in file_visitor.find_imported_objects().keys():
            module_name = file_visitor.find_imported_objects()[object_name]
            try:
                return ModuleHelper.get_module_file_from_name(object_name, module_name)
            except Exception as e:
                print(e, traceback.print_exc())

        # Check if the __init__ file contains the definition
        if not os.path.isfile(generated_path):
            raise Exception(f"No matching file for {generated_path}")
        return generated_path


class FileVisitor:

    def __init__(self, *args, **kwargs):
        self.file_path: str = kwargs["file_path"]
        self.module_name: str = ModuleHelper.get_module_name_from_file(self.file_path)
        with open(self.file_path, "r") as source:
            self.code: str = source.read()
            self.tree = ast.parse(self.code)
        self.import_analyzer = ImportAnalyzer(
            object_name=kwargs.get("object_name"), module_name=self.module_name
        )

    def find_imported_objects(self) -> dict[str, str]:
        self.import_analyzer.visit(self.tree)
        return self.import_analyzer.object_module_mapping

    def _get_code_segment(self, node: Any) -> str:
        code: str = ast.unparse(node)
        return code

    def find_defined_object(self) -> str:
        self.import_analyzer.visit(self.tree)
        node_obj = self.import_analyzer.defined_objects.get(self.import_analyzer.object_name)
        if not node_obj:
            print(f"Node not found for object {self.import_analyzer.object_name} at {self.file_path}")
            return ""
        return self._get_code_segment(node_obj)


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
