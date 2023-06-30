import os
import ast
import traceback

from typing import Any

from import_analyzer import ImportAnalyzer


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
