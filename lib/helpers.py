import os
import pandas as pd
import datetime

from lib.variable_names import Variables


"""
This module contains small functions that will be frequently re-used within the project.
"""


class DataRoot:
    """
    Provides relative root paths of the project.
    This helps avoid using absolute paths, which makes the code unusable in another computer.
    """

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.raw_data_root = os.path.join(self.project_root, 'data', 'raw_data')
        self.cleaned_data_root = os.path.join(self.project_root, 'data', 'cleaned_data')

        # overall company info (from Bloomberg)
        self.company_info = pd.read_excel(os.path.join(self.raw_data_root, Variables.BloombergDB.FILES.RAW_DATA_FILE_NAME),
                                          sheet_name=Variables.BloombergDB.FILES.COMPANY_INFO_SHEET_NAME)


class SmallFunction:
    """
    Provides small functions that can be used to clean data.
    """

    @staticmethod
    def generate_series(start_dt: datetime.date, end_dt: datetime.date):
        """
        Generates a dataframe having continuous lists of month and year from start_dt to end_dt.
        """
        if not isinstance(start_dt, datetime.date) or not isinstance(end_dt, datetime.date):
            raise TypeError

        series = pd.date_range(start=start_dt, end=end_dt, freq='1M').to_frame()
        series['month'] = series[0].dt.month
        series['year'] = series[0].dt.year
        series = series[['month', 'year']].reset_index(drop=True)

        return series


class ExtractData(DataRoot):
    """
    This class extracts cleaned data and regression data.
    """

    def __init__(self):
        super().__init__()
        self.cleaned_file_name = Variables.CleanedData.FILE_NAME
        self.h1_file_name = Variables.RegressionData.FILES.H1_FILE_NAME
        self.h2_file_name = Variables.RegressionData.FILES.H2_FILE_NAME

    def extract_cleaned_data(self):
        """
        :return a dictionary contains dataframes of (cleaned) ESG ratings of each rating provider,
        S&P credit ratings, and accounting data. The dictionary has the following keys:

            - 'sustainalytics': Sustainalytics ESG ratings
            - 'spglobal': S&P Global (RobecoSAM) ESG ratings
            - 'refinitiv': Refinitiv ESG ratings
            - 'populated_sp': populated S&P credit ratings
            - 'control_var': populated control variables
        """
        esg_bb = pd.read_excel(os.path.join(self.cleaned_data_root, self.cleaned_file_name),
                               sheet_name=Variables.CleanedData.BLOOMBERG_ESG_SHEET_NAME)

        # get data of Sustainalytics ESG ratings
        sustainalytics = esg_bb.loc[esg_bb[Variables.SustainalyticsESG.TOTAL].notnull()]
        sustainalytics = sustainalytics.drop(columns=[
            Variables.SPGlobalESG.TOTAL,
            Variables.SPGlobalESG.ENV,
            Variables.SPGlobalESG.ECON,
            Variables.SPGlobalESG.SOCIAL
        ])

        # get data of S&P Global (RobecoSAM) ESG ratings
        spglobal = esg_bb.loc[esg_bb[Variables.SPGlobalESG.TOTAL].notnull()]
        spglobal = spglobal.drop(columns=[
            Variables.SustainalyticsESG.TOTAL,
            Variables.SustainalyticsESG.ENV,
            Variables.SustainalyticsESG.SOCIAL,
            Variables.SustainalyticsESG.GOV
        ])

        # get data of Refinitiv ESG ratings
        refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, self.cleaned_file_name),
                                  sheet_name=Variables.CleanedData.REFINITIV_ESG_SHEET_NAME)

        # get data of populated S&P credit ratings
        populated_sp = pd.read_excel(os.path.join(self.cleaned_data_root, self.cleaned_file_name),
                                     sheet_name=Variables.CleanedData.POPULATED_SP_CREDIT_RTG_SHEET_NAME)

        # get data of populated control variables
        control_var = pd.read_excel(os.path.join(self.cleaned_data_root, self.cleaned_file_name),
                                    sheet_name=Variables.CleanedData.POPULATED_ACCOUNTING_SHEET_NAME)

        return {'spglobal': spglobal,
                'sustainalytics': sustainalytics,
                'refinitiv': refinitiv,
                'populated_sp': populated_sp,
                'control_var': control_var}

    def extract_regression_data(self):
        """
        Returns a dictionary contain regression data for each hypothesis.
        Executing this function can result in long waiting time due to many large data frames.
        """

        # hypothesis 1 - Refinitiv dataset
        h1_refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, self.h1_file_name),
                                     sheet_name=Variables.RegressionData.FILES.H1_REFINITIV_SHEET_NAME)
        h1_refinitiv.rename(columns={
            Variables.RefinitivESG.TOTAL: Variables.RegressionData.IndependentVar.H1_ESG_RTG,
            Variables.RefinitivESG.ENV: Variables.RegressionData.IndependentVar.H1_ESG_ENV,
            Variables.RefinitivESG.SOCIAL: Variables.RegressionData.IndependentVar.H1_ESG_SOC,
            Variables.RefinitivESG.GOV: Variables.RegressionData.IndependentVar.H1_ESG_GOV,
            'ordinal_rating': Variables.RegressionData.DependentVar.H1_CREDIT_RTG
        }, inplace=True)

        # hypothesis 1 - S&P Global data
        h1_spglobal = pd.read_excel(os.path.join(self.cleaned_data_root, self.h1_file_name),
                                    sheet_name=Variables.RegressionData.FILES.H1_SPGLOBAL_SHEET_NAME)
        h1_spglobal.rename(columns={
            Variables.SPGlobalESG.TOTAL: Variables.RegressionData.IndependentVar.H1_ESG_RTG,
            Variables.SPGlobalESG.ENV: Variables.RegressionData.IndependentVar.H1_ESG_ENV,
            Variables.SPGlobalESG.SOCIAL: Variables.RegressionData.IndependentVar.H1_ESG_SOC,
            Variables.SPGlobalESG.ECON: Variables.RegressionData.IndependentVar.H1_ESG_GOV,
            'ordinal_rating': Variables.RegressionData.DependentVar.H1_CREDIT_RTG
        }, inplace=True)

        # hypothesis 1 - Sustainalytics data
        h1_sustainalytics = pd.read_excel(os.path.join(self.cleaned_data_root, self.h1_file_name),
                                          sheet_name=Variables.RegressionData.FILES.H1_SUSTAINALYTICS_SHEET_NAME)
        h1_sustainalytics.rename(columns={
            Variables.SustainalyticsESG.TOTAL: Variables.RegressionData.IndependentVar.H1_ESG_RTG,
            Variables.SustainalyticsESG.ENV: Variables.RegressionData.IndependentVar.H1_ESG_ENV,
            Variables.SustainalyticsESG.SOCIAL: Variables.RegressionData.IndependentVar.H1_ESG_SOC,
            Variables.SustainalyticsESG.GOV: Variables.RegressionData.IndependentVar.H1_ESG_GOV,
            'ordinal_rating': Variables.RegressionData.DependentVar.H1_CREDIT_RTG
        }, inplace=True)

        # hypothesis 2 - monthly data
        h2_monthly = pd.read_excel(os.path.join(self.cleaned_data_root, self.h2_file_name),
                                   sheet_name=Variables.RegressionData.FILES.H2_MONTHLY_DATA_SHEET_NAME)

        # hypothesis 2 - yearly data
        h2_yearly = pd.read_excel(os.path.join(self.cleaned_data_root, self.h2_file_name),
                                  sheet_name=Variables.RegressionData.FILES.H2_YEARLY_DATA_SHEET_NAME)

        # hypothesis 2 - main data
        h2_main = pd.read_excel(os.path.join(self.cleaned_data_root, self.h2_file_name),
                                sheet_name=Variables.RegressionData.FILES.H2_MAIN_DATA_SHEET_NAME)

        return {
            'h1_refinitiv': h1_refinitiv,
            'h1_spglobal': h1_spglobal,
            'h1_sustainalytics': h1_sustainalytics,
            'h2_monthly': h2_monthly,
            'h2_yearly': h2_yearly,
            'h2_main': h2_main,
        }


if __name__ == "__main__":
    # ExtractData().extract_cleaned_data()
    # ExtractData().extract_regression_data()
    pass
