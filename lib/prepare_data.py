import pandas as pd
from datetime import date

from lib.helpers import ExtractData, SmallFunction
from lib.variable_names import Variables


class PrepareData:
    """
    Prepare data for getting descriptive statistics and running regression
    """

    def __init__(self):
        super().__init__()
        self.cleaned_data_dict = ExtractData().extract_cleaned_data()
        self.timerange = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

    def control(self):
        pass

    def h1_refinitiv(self):
        """
        Retrieve all data necessary to run hypothesis 1 for Refinitiv ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        refinitiv = self.cleaned_data_dict['refinitiv']
        refinitiv = refinitiv.drop(columns=['ID_ISIN', 'Dates'])

        data = []
        for company in refinitiv[Variables.Bloomberg.BB_TICKER].unique():
            df = refinitiv.loc[refinitiv[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.dropna(how='any')
        data = data.loc[data['ordinal_rating'] != 0]

        return data

    def h1_sustainalytics(self):
        """
        Retrieve all data necessary to run hypothesis 1 for Sustainalytics ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        sustainalytics = self.cleaned_data_dict['sustainalytics']
        sustainalytics = sustainalytics.drop(columns=[
            'Dates',
            Variables.SPGlobalESG.ENV,
            Variables.SPGlobalESG.ECON,
            Variables.SPGlobalESG.SOCIAL,
            Variables.SPGlobalESG.TOTAL,
        ])

        data = []
        for company in sustainalytics[Variables.Bloomberg.BB_TICKER].unique():
            df = sustainalytics.loc[sustainalytics[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.dropna(how='any')
        data = data.loc[data['ordinal_rating'] != 0]

        return data

    def h1_spglobal(self):
        """
        Retrieve all data necessary to run hypothesis 1 for S&P Global ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        spglobal = self.cleaned_data_dict['robecosam']
        spglobal = spglobal.drop(columns=[
            'Dates',
            Variables.SustainalyticsESG.ENV,
            Variables.SustainalyticsESG.SOCIAL,
            Variables.SustainalyticsESG.GOV,
            Variables.SustainalyticsESG.TOTAL,
        ])

        data = []
        for company in spglobal[Variables.Bloomberg.BB_TICKER].unique():
            df = spglobal.loc[spglobal[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.dropna(how='any')
        data = data.loc[data['ordinal_rating'] != 0]

        return data


if __name__ == "__main__":
    PrepareData().control()
    pass
