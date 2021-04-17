import pandas as pd
from scipy import stats

from lib.variable_names import Variables
from lib.helpers import ExtractData


class Regression:

    def __init__(self):
        self.regression_data_dict = ExtractData().extract_regression_data()

    def control(self):
        pass


if __name__ == "__main__":
    Regression().control()
    # AnalyseData().corr(data=AnalyseData().regression_data_dict['h1_refinitiv'])
    pass