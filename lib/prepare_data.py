import os
import pandas as pd
from datetime import date

from lib.clean_data import CleanBase
from lib.analyse_data import AnalyseData


class PrepareData(CleanBase):
    """
    Prepare data for getting descriptive statistics and running regression
    """

    def __init__(self):
        super().__init__()
        self.cleaned_data_dict = AnalyseData().extract_cleaned_data()
        self.timerange = self.generate_timerange()

    def control(self):
        pass

    @staticmethod
    def generate_timerange():
        """
        Returns a dataframe with month and year from 2006 to 2020
        """
        daterange = pd.date_range(start=date(2006, 1, 1), end=date(2020, 12, 31), freq='1M').to_frame()
        daterange['month'] = daterange[0].dt.month
        daterange['year'] = daterange[0].dt.year
        daterange = daterange[['month', 'year']].reset_index(drop=True)

        return daterange

    def h1_refinitiv(self):
        """
        Retrieve all data necessary to run hypothesis 1 for Refinitiv ESG scores
        Null values is excluded.
        """
        refinitiv = self.cleaned_data_dict['refinitiv']
        refinitiv['month'] = refinitiv['Dates'].dt.month
        refinitiv['year'] = refinitiv['Dates'].dt.year
        refinitiv = refinitiv.drop(columns=['ID_ISIN', 'Dates'])

        data = []
        for company in refinitiv['Fundamental Ticker Equity'].unique():
            df = refinitiv.loc[refinitiv['Fundamental Ticker Equity'] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)


        populated_sp = self.cleaned_data_dict['populated_sp']
        populated_sp = populated_sp.rename(columns={'rating_month': 'month', 'rating_year': 'year'})
        data = data.merge(populated_sp, on=['month', 'year', 'Fundamental Ticker Equity'], how='left')

        control_var = self.cleaned_data_dict['control_var']

        control_var['month'] = control_var['Dates'].dt.month
        control_var['year'] = control_var['Dates'].dt.year
        control_var = control_var.drop(columns=['Dates'])

        populated_control_var = []
        for company in control_var['Fundamental Ticker Equity'].unique():
            df = control_var.loc[control_var['Fundamental Ticker Equity'] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            df = df.fillna(method='bfill')  # use next valid observation to fill gap.
            populated_control_var.append(df)
        populated_control_var = pd.concat(populated_control_var)
        populated_control_var = populated_control_var.dropna(how='any')

        data = data.merge(populated_control_var, on=['month', 'year', 'Fundamental Ticker Equity'], how='left')

        data = data.dropna(how='any')

        return data


# PrepareData().h1_refinitiv()
