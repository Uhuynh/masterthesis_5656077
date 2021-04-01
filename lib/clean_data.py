import os
from datetime import date
import pandas as pd
import numpy as np

from lib.variable_names import Variables


class CleanBase:
    """
    This class provides an overview of standard ETL procedure for cleaning the raw data:
        1. Extract raw data downloaded from Bloomberg/Refinitiv in Excel
        2. Transform data (from wide to long format)
        3. Load transformed data by exporting to Excel files.
    """

    def __init__(self):

        # data path
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.raw_data_root = os.path.join(self.project_root, 'data', 'raw_data')
        self.cleaned_data_root = os.path.join(self.project_root, 'data', 'cleaned_data')

        # overall company info (from Bloomberg)
        self.company_info = pd.read_excel(os.path.join(self.raw_data_root, Variables.Bloomberg.FILE_NAME),
                                          sheet_name=Variables.Bloomberg.COMPANY_INFO_SHEET_NAME)

    def extract_data(self, file_name: str, sheet_name: str):
        return pd.read_excel(os.path.join(self.raw_data_root, file_name), sheet_name=sheet_name)

    def transform_data(self, data):
        return data

    @staticmethod
    def load_data(data, file_name: str, sheet_name: str):
        with pd.ExcelWriter(file_name) as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)


class Helper:
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




class BloombergESG(CleanBase):
    """
    Clean S&P Global (RobecoSAM) and Sustainalytics ESG data downloaded from Bloomberg.
    """

    def __init__(self):
        super().__init__()

    def control(self):
        data = self.extract_data(file_name=Variables.Bloomberg.FILE_NAME,
                                 sheet_name=Variables.Bloomberg.ESG_SHEET_NAME)
        data_t = self.transform_data(data)
        self.load_data(transformed_data=data_t,
                       file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.BLOOMBERG_ESG_SHEET_NAME)

    def transform_data(self, data):
        # fill BB_Ticker to missing places
        data.iloc[2, :] = data.iloc[2, :].fillna(method='ffill', axis=0)

        data = data.rename(columns=data.iloc[2])  # rename columns to BB_Tickers

        data = data.iloc[4:, :]  # remove redundant headers

        # reset index to 'Dates'
        data = data.reset_index(drop=True)
        data = data.rename(columns={data.columns[0]: 'Dates'})
        data = data.set_index('Dates')

        # reshape data (also drop NA values)
        temp = data.T
        temp = temp.set_index(['Dates'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={
            temp.columns[0]: Variables.Bloomberg.BB_TICKER,
            temp.columns[1]: 'variable'})

        data_t = temp.melt(id_vars=[Variables.Bloomberg.BB_TICKER, 'variable'], var_name='Dates')
        data_t = pd.pivot_table(
            data_t,
            values='value',
            index=[Variables.Bloomberg.BB_TICKER, 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        data_t = data_t.reset_index()
        data_t = data_t.rename(columns={
            data_t.columns[0]: Variables.Bloomberg.BB_TICKER,
            data_t.columns[1]: 'Dates'
        })

        # extract month and year from reported days
        # which will be used for merging data to run regression
        data_t['Dates'] = pd.to_datetime(data_t['Dates'])
        data_t['month'] = data_t['Dates'].dt.month
        data_t['year'] = data_t['Dates'].dt.year
        data_t['Dates'] = data_t['Dates'].dt.date

        # sort values by dates
        data_t = data_t.sort_values([Variables.Bloomberg.BB_TICKER, 'Dates'], ascending=True)

        return data_t


class RefinitivESG(CleanBase):
    """
    Clean ESG data downloaded from Refinitiv.
    """

    def __init__(self):
        super().__init__()

    def control(self):
        data = self.extract_data(file_name=Variables.Refinitiv.FILE_NAME,
                                 sheet_name=Variables.Refinitiv.ESG_SHEET_NAME)
        data_t = self.transform_data(data)
        self.load_data(transformed_data=data_t,
                       file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.REFINITIV_ESG_SHEET_NAME)

    def transform_data(self, data):
        data = data.set_index('Name')  # set index

        # rename columns and esg variables
        df = data.iloc[0, :]
        df = df.reset_index(drop=True)
        df = df.to_frame()
        df = df.assign(list=df['Code'].str.split("(")).explode("list")
        df = df.reset_index(drop=True)
        column_names = df["list"].iloc[::2]  # extract even indexes
        variable_names = df["list"].iloc[1::2]  # extract odd indexes

        data.columns = list(column_names)
        data.loc["Code", :] = list(variable_names)

        # rename index to 'Dates'
        data = data.reset_index()
        data = data.rename(columns={data.columns[0]: 'Dates'})
        data = data.set_index('Dates')

        # reshape data (also drop NA values)
        temp = data.T
        temp = temp.set_index(['Code'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={temp.columns[0]: 'company_isin', temp.columns[1]: 'variable'})

        data_t = temp.melt(id_vars=['company_isin', 'variable'], var_name='Dates')
        data_t = pd.pivot_table(
            data_t,
            values='value',
            index=['company_isin', 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        data_t = data_t.reset_index()

        # extract month and year from reported date
        data_t['Dates'] = pd.to_datetime(data_t['Dates'])
        data_t['month'] = data_t['Dates'].dt.month
        data_t['year'] = data_t['Dates'].dt.year
        data_t['Dates'] = data_t['Dates'].dt.date

        # sort values
        data_t = data_t.sort_values(['company_isin', 'Dates'], ascending=True)
        data_t = data_t.rename(columns={'company_isin': 'ID_ISIN'})

        # merge with 'company_info.xlsx' to get BB_TICKER
        data_t = data_t.merge(self.company_info[[Variables.Bloomberg.BB_TICKER, 'ID_ISIN']], on='ID_ISIN', how='outer')
        data_t = data_t.loc[data_t['Dates'].notnull()]

        # shift Dates to 1 day backward to get end-of-month rating
        data_t['Dates'] = data_t['Dates'] - pd.Timedelta('1 day')

        # exclude data before 2006
        data_t = data_t.loc[data_t['Dates'] > date(2005, 12, 31)].reset_index(drop=True)

        # exclude data that are not in selected companies sample
        data_t = data_t.loc[data_t[Variables.Bloomberg.BB_TICKER].notnull()]

        return data_t


class BloombergCreditRtg(CleanBase):
    """
    Clean S&P credit rating changes downloaded from Bloomberg
    and merge with credit rating provided from supervisor.
    """

    def __init__(self):
        super().__init__()

    def control(self):
        supervisor_data = self.extract_data(file_name=Variables.SupervisorData.FILE_NAME,
                                            sheet_name=Variables.SupervisorData.SHEET_NAME)
        data_t = self.transform_data(supervisor_data)
        result = self.hard_code_rating(data_t)
        self.load_data(transformed_data=result, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.SP_CREDIT_RTG_SHEET_NAME)
        populated_rtg = self.populate_rtg(result)
        self.load_data(transformed_data=populated_rtg, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.POPULATED_SP_CREDIT_RTG_SHEET_NAME)

    def transform_data(self, supervisor_data):
        ##################################
        # transform data provided by Zorka
        ##################################

        # merge credit ratings (from Zorka) to selected companies
        data = self.company_info[['companyid', Variables.Bloomberg.BB_TICKER]].merge(
            supervisor_data[['companyid', 'rating_date', 'rating']], on='companyid', how='left')

        # remove NAs
        data = data.loc[data['rating'].notnull()]
        data['rating_date'] = data['rating_date'].dt.date

        ###############################
        # transform data from Bloomberg
        ###############################

        # get rating changes from Bloomberg
        rating_changes_bb = self.extract_data(file_name=Variables.Bloomberg.FILE_NAME,
                                              sheet_name=Variables.Bloomberg.SP_RATING_CHANGES_SHEET_NAME)

        # only get LT Foreign Rating
        rating_changes_bb = rating_changes_bb.loc[rating_changes_bb['Rating Type'] == Variables.SPCreditRtg.LT_FOREIGN_ISSUER]

        # retrieve rating after change
        rating_changes_bb[['rating', 'outlook']] = rating_changes_bb['Curr Rtg'].str.split(' ', 1, expand=True)
        rating_changes_bb = rating_changes_bb[['Date', 'rating', 'Security Name']]

        rating_changes_bb['Date'] = pd.to_datetime(rating_changes_bb['Date'])
        rating_changes_bb['Date'] = rating_changes_bb['Date'].dt.date

        rating_changes_bb = rating_changes_bb.rename(columns={'Date': 'rating_date',
                                                              'Security Name': Variables.Bloomberg.BB_TICKER})

        ###################################
        # merge data from Zorka & Bloomberg
        ###################################
        data_t = data.merge(rating_changes_bb, how='outer', on=[Variables.Bloomberg.BB_TICKER, 'rating_date', 'rating'])
        data_t = data_t.sort_values([Variables.Bloomberg.BB_TICKER, 'rating_date'], ascending=True)

        data_t = data_t.drop(columns=['companyid'])
        data_t = data_t.drop_duplicates(keep='first')

        return data_t

    @staticmethod
    def hard_code_rating(data):
        """
        Transform credit rating to an ordinal scale
            - NR: rating has not been assigned or is no longer assigned.
        """
        data.loc[data['rating'] == 'NR', 'ordinal_rating'] = 0
        data.loc[data['rating'] == 'D', 'ordinal_rating'] = 1
        data.loc[data['rating'] == 'SD', 'ordinal_rating'] = 1
        data.loc[data['rating'] == 'C', 'ordinal_rating'] = 2
        data.loc[data['rating'] == 'CC', 'ordinal_rating'] = 2
        data.loc[data['rating'] == 'CCC-', 'ordinal_rating'] = 3
        data.loc[data['rating'] == 'CCC', 'ordinal_rating'] = 3
        data.loc[data['rating'] == 'CCC+', 'ordinal_rating'] = 3
        data.loc[data['rating'] == 'B-', 'ordinal_rating'] = 4
        data.loc[data['rating'] == 'B', 'ordinal_rating'] = 4
        data.loc[data['rating'] == 'B+', 'ordinal_rating'] = 4
        data.loc[data['rating'] == 'BB-', 'ordinal_rating'] = 5
        data.loc[data['rating'] == 'BB', 'ordinal_rating'] = 5
        data.loc[data['rating'] == 'BB+', 'ordinal_rating'] = 5
        data.loc[data['rating'] == 'BBB-', 'ordinal_rating'] = 6
        data.loc[data['rating'] == 'BBB', 'ordinal_rating'] = 6
        data.loc[data['rating'] == 'BBB+', 'ordinal_rating'] = 6
        data.loc[data['rating'] == 'A-', 'ordinal_rating'] = 7
        data.loc[data['rating'] == 'A', 'ordinal_rating'] = 7
        data.loc[data['rating'] == 'A+', 'ordinal_rating'] = 7
        data.loc[data['rating'] == 'AA-', 'ordinal_rating'] = 8
        data.loc[data['rating'] == 'AA', 'ordinal_rating'] = 8
        data.loc[data['rating'] == 'AA+', 'ordinal_rating'] = 8
        data.loc[data['rating'] == 'AAA', 'ordinal_rating'] = 9

        return data

    @staticmethod
    def populate_rtg(data):
        """
        Populate credit ratings to monthly data from 2006 - 2020.
        """

        data['rating_date'] = pd.to_datetime(data['rating_date'])

        # extract month and year from rating_date
        data['month'] = data['rating_date'].dt.month
        data['year'] = data['rating_date'].dt.year

        series = Helper.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

        ########################
        # populate credit rating
        ########################
        rating = data.drop(columns=['rating_date', 'rating'])

        # drop duplicated rating
        # there are cases when companies have credit rating changes more than one time within a month
        # but these cases are very rare, and thus we only keep the latest value within that month
        rating = rating.drop_duplicates(keep='last')

        # populate (this also excludes data after 2020)
        populated_rtg = []
        for company in rating[Variables.Bloomberg.BB_TICKER].unique():
            df = rating.loc[rating[Variables.Bloomberg.BB_TICKER] == company]
            df = series.merge(df, on=['month', 'year'], how='outer')
            df = df.fillna(method='ffill')  # propagate last valid observation forward to next valid
            populated_rtg.append(df)
        populated_rtg = pd.concat(populated_rtg)

        # only get data between 2006 and 2020
        populated_rtg = populated_rtg.loc[(populated_rtg['year'] >= 2006) & (populated_rtg['year'] <= 2020)]

        # drop NA values
        populated_rtg = populated_rtg.dropna(axis=0, how='any')

        return populated_rtg


class BloombergAccounting(CleanBase):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        accounting_data = self.extract_data(file_name='raw_data_bloomberg_march.xlsx', sheet_name='accounting yearly')

        transformed_data = self.transform_data(accounting_data)
        self.load_data(transformed_data=transformed_data,
                       file_name='cleaned_data.xlsx',
                       sheet_name='accounting_data')

        data = self.calculate_control_var(transformed_data)
        result = self.clean(data)
        self.load_data(transformed_data=result,
                       file_name='cleaned_data.xlsx',
                       sheet_name='control_var')

    def transform_data(self, accounting_data):
        """
        Transform accounting data from wide to long format.
        """

        # fill fundamental ticker to missing places
        accounting_data.iloc[2, :] = accounting_data.iloc[2, :].fillna(method='ffill', axis=0)

        # rename columns
        accounting_data = accounting_data.rename(columns=accounting_data.iloc[2])

        # remove redundant headers
        accounting_data = accounting_data.iloc[4:, :]
        accounting_data = accounting_data.reset_index(drop=True)

        # reset index
        accounting_data = accounting_data.rename(columns={accounting_data.columns[0]: 'Dates'})
        accounting_data = accounting_data.set_index('Dates')

        # reshape data (also drop NA values)
        temp = accounting_data.T
        temp = temp.set_index(['Dates'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={temp.columns[0]: 'company_name', temp.columns[1]: 'variable'})

        data = temp.melt(id_vars=['company_name', 'variable'], var_name='Dates')
        data = pd.pivot_table(
            data,
            values='value',
            index=['company_name', 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        data = data.reset_index()
        data = data.rename(columns={data.columns[0]: 'company_name', data.columns[1]: 'Dates'})
        data['Dates'] = pd.to_datetime(data['Dates'])
        data['Dates'] = data['Dates'].dt.date

        # sort values
        data = data.sort_values(['company_name', 'Dates'], ascending=True)
        data = data.rename(columns={'company_name': 'Fundamental Ticker Equity'})

        return data

    @staticmethod
    def calculate_control_var(data):
        """
        Calculate additional control variables
            - SIZE = natural log of Total Assets
            - LEVERAGE = (Long-term Borrowing / Total Assets) * 100
            - ROA = (EBIT / Total Assets) * 100
        """
        data['SIZE'] = np.log(data['BS_TOT_ASSET'])
        data['LEVERAGE'] = (data['BS_LT_BORROW'] / data['BS_TOT_ASSET']) * 100
        data['ROA'] = (data['EBIT'] / data['BS_TOT_ASSET']) * 100

        return data

    @staticmethod
    def clean(transformed_data):
        """
        Exclude companies that do not have enough control variables
        """
        data = transformed_data[['SIZE',
                                 'LEVERAGE',
                                 'ROA',
                                 'OPER_MARGIN',
                                 'INTEREST_COVERAGE_RATIO',
                                 'Fundamental Ticker Equity',
                                 'Dates']]

        # drop row that has NA values
        data = data.dropna(axis=0, how='any')

        return data




if __name__ == "__main__":
    # BloombergESG().control()
    # RefinitivESG().control()
    BloombergCreditRtg().control()
    # AccountingData().control()
    pass
