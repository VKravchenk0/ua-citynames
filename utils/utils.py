import os
import shutil
from pathlib import Path
import settings


class FileUtils:

    @staticmethod
    def get_output_file_name():
        filename = 'result_dev.txt' if settings.dev else 'result.txt'
        return f"{settings.base_output_dir}/{filename}"

    def reset_output_directory(self):
        self.delete_output_dir_if_exists()
        self.create_output_dir()

    @staticmethod
    def delete_output_dir_if_exists():
        dirpath = Path(settings.base_output_dir)
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)

    def create_output_dir(self):
        filename = self.get_output_file_name()
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    @staticmethod
    def get_input_file_path():
        if settings.dev:
            return './input_files/dev_koatuu.json'
        return './input_files/koatuu.json'
