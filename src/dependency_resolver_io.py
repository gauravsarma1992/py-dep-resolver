import os


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
