import os
import shutil
from pathlib import Path
import settings


class FileUtils:

    @staticmethod
    def get_output_file_path(filename):
        filename_with_extension = filename + ('_dev.txt' if settings.dev else '.txt')
        return f"{settings.base_output_dir}/{filename_with_extension}"

    def reset_output_directory(self):
        self.delete_output_dir_if_exists()

    @staticmethod
    def delete_output_dir_if_exists():
        dirpath = Path(settings.base_output_dir)
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)

    def create_output_dir(self, filename):
        filename = self.get_output_file_path(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    @staticmethod
    def get_input_file_path():
        if settings.dev:
            return './input_files/dev_koatuu.json'
        return './input_files/koatuu.json'
