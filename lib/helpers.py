import os
import pandas as pd
from datetime import date

from lib.variable_names import Variables


"""
This module contains small functions that will be frequently re-used within the project.
"""


class DataRoot:
    """
    Provides data root paths.
    """

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.raw_data_root = os.path.join(self.project_root, 'data', 'raw_data')
        self.cleaned_data_root = os.path.join(self.project_root, 'data', 'cleaned_data')

        # overall company info (from Bloomberg)
        self.company_info = pd.read_excel(os.path.join(self.raw_data_root, Variables.Bloomberg.FILE_NAME),
                                          sheet_name=Variables.Bloomberg.COMPANY_INFO_SHEET_NAME)


class SmallFunction:
    """
    Provides small functions that can be used to clean data.
    """

    @staticmethod
    def generate_series(start_dt: date, end_dt: date):
        """
        Generates a dataframe having continuous lists of month and year from start_dt to end_dt.
        """
        if not isinstance(start_dt, date) or not isinstance(end_dt, date):
            raise TypeError

        series = pd.date_range(start=start_dt, end=end_dt, freq='1M').to_frame()
        series['month'] = series[0].dt.month
        series['year'] = series[0].dt.year
        series = series[['month', 'year']].reset_index(drop=True)

        return series


class ExtractData(DataRoot):
    """
    Extract cleaned data and regression data
    """
    def __init__(self):
        super().__init__()

    def extract_cleaned_data(self):
        """
        Return a dictionary contains (cleaned) ESG ratings, credit ratings of each provider and accounting data.
            - sustainalytics: Sustainalytics ESG rating
            - robecosam: RobecoSAM (S&P Global) ESG rating
            - refinitiv: Refinitiv ESG rating
            - populated_sp: populated S&P credit rating
            - control_var: control variables
        """
        esg_bb = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                               sheet_name=Variables.CleanedData.BLOOMBERG_ESG_SHEET_NAME)

        # get companies with Sustainalytics ESG ratings
        sustainalytics = esg_bb.loc[esg_bb[Variables.SustainalyticsESG.TOTAL].notnull()]

        # get companies with RobecoSAM ESG ratings
        robecosam = esg_bb.loc[esg_bb[Variables.SPGlobalESG.TOTAL].notnull()]

        # get companies with Refinitiv ESG ratings
        refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                                  sheet_name=Variables.CleanedData.REFINITIV_ESG_SHEET_NAME)

        # get companies with populated S&P credit rating
        populated_sp = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                                     sheet_name=Variables.CleanedData.POPULATED_SP_CREDIT_RTG_SHEET_NAME)

        # get populated control variables of companies
        control_var = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                                    sheet_name=Variables.CleanedData.POPULATED_ACCOUNTING_SHEET_NAME)

        return {'robecosam': robecosam,
                'sustainalytics': sustainalytics,
                'refinitiv': refinitiv,
                'populated_sp': populated_sp,
                'control_var': control_var}

    def extract_regression_data(self):
        """
        Returns a dictionary contain regression data for each hypothesis,
        separated by each ESG rating providers.
        """
        h1_refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.FILE_NAME),
                                     sheet_name=Variables.RegressionData.H1_REFINITIV_SHEET_NAME)

        h1_spglobal = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.FILE_NAME),
                                    sheet_name=Variables.RegressionData.H1_SPGLOBAL_SHEET_NAME)

        h1_sustainalytics = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.FILE_NAME),
                                          sheet_name=Variables.RegressionData.H1_SUSTAINALYTICS_SHEET_NAME)

        return {
            'h1_refinitiv': h1_refinitiv,
            'h1_spglobal': h1_spglobal,
            'h1_sustainalytics': h1_sustainalytics
        }
