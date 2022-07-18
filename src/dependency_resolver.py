import os
import traceback
from io import BytesIO
from tokenize import tokenize, NAME

from import_analyzer import ModuleHelper, FileVisitor


RESOLVED_LIST=set()

class Tokenizer:
    def __init__(self, *args, **kwargs):
        self.code: str = kwargs["code"]

    def tokenize(self) -> set[str]:
        tokens = tokenize(BytesIO(self.code.encode('utf-8')).readline)
        token_set = set()
        for toknum, tokval, _, _, _ in tokens:
            if toknum == NAME:
                token_set.add(tokval)

        return token_set


class DependencyResolverIO:
    def __init__(self, *args, **kwargs):
        self.output_folder: str = kwargs.get("output_folder", "/tmp/core")
        self.resolve_for_obj: str = kwargs["resolve_for_obj"]

        self._pre_process()

    def _pre_process(self) -> None:
        self._clean_folder(self.output_folder)
        self._mkdir(self.output_folder)

    def _clean_folder(self, folder_path: str) -> None:
        import shutil
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

    def _mkdir(self, folder_path: str) -> None:
        os.makedirs(folder_path, exist_ok=True)

    def _resolve_obj(self) -> [str, str]:
        file_path, object_name = self.resolve_for_obj.split("::")
        return file_path, object_name


class DependencyResolverManager:
    def __init__(self, *args, **kwargs):
        self.file_path: str
        self.object_name: str
        self.io: "DependencyResolverIO" = DependencyResolverIO(*args, **kwargs)
        self.resolve_for_obj: str = kwargs.get("resolve_for_obj")
        self.resolve_count: int = kwargs.get("resolve_count", 0)
        self.file_path, self.object_name = self.io._resolve_obj()
        print(f"Resolving object - {self.resolve_for_obj} | Depth - {self.resolve_count}")

    def _resolve_imports(self, file_path: str) -> dict[str, str]:
        file_visitor: "FileVisitor" = FileVisitor(file_path=file_path)
        return file_visitor.find_imported_objects()

    def _find_object_code(self, file_path: str, object_name: str) -> str:
        file_visitor: "FileVisitor" = FileVisitor(file_path=file_path, object_name=object_name)
        return file_visitor.find_defined_object()

    def _resolve_matching_objects(self, object_code: str, imported_objects: dict[str, str]):
        imported_objects_set: set[str] = set(imported_objects.keys())
        tokenizer: "Tokenizer" = Tokenizer(code=object_code)
        matching_objects: list["DependencyResolverManager"] = []

        for matched_object in imported_objects_set.intersection(tokenizer.tokenize()):
            matched_module: str = imported_objects[matched_object]
            file_path: str
            try:
                file_path = ModuleHelper.get_module_file_from_name(matched_object, matched_module)
                resolve_for_obj: str = f"{file_path}::{matched_object}"
                resolver: "DependencyResolverManager" = DependencyResolverManager(
                    resolve_for_obj=resolve_for_obj, resolve_count=self.resolve_count
                )
                resolver.process_obj()
            except Exception as e:
                print(e, matched_object, matched_module, traceback.print_exc())
                continue

    def process_obj(self) -> None:
        global RESOLVED_LIST

        if self.resolve_for_obj in RESOLVED_LIST:
            #print(f"Object for {self.resolve_for_obj} already resolved")
            return

        self.resolve_count += 1
        if self.resolve_count > 30:
            print(f"Deep loop detected for {self.resolve_for_obj}")
            return

        imported_objects: dict[str, str] = self._resolve_imports(self.file_path)
        RESOLVED_LIST.add(self.resolve_for_obj)
        self._resolve_matching_objects(
            self._find_object_code(self.file_path, self.object_name), imported_objects
        )
        print(f"Completed resolving object - {self.resolve_for_obj} | Depth - {self.resolve_count}")



if __name__ == "__main__":
    base_dir: str = os.environ.get("BASE_DIR", "")
    file_path: str = os.environ.get("FILE_PATH", "")
    resolve_for_obj: str = f"{base_dir}/{file_path}/models/__init__.py::Address"
    resolver = DependencyResolverManager(resolve_for_obj=resolve_for_obj)
    resolver.process_obj()
