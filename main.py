import pandas as pd

from analyzer.city_name_analyzer import CityNameAnalyzer
from utils.utils import FileUtils

file_utils = FileUtils()
file_utils.reset_output_directory()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

CityNameAnalyzer().process_dataset(file_utils.get_input_file_path())
