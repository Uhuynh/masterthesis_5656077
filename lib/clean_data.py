import os
from datetime import date
import pandas as pd
import numpy as np

from lib.variable_names import Variables
from lib.helpers import DataRoot, SmallFunction


class CleanBase(DataRoot):
    """
    This class provides an overview of standard ETL procedure for cleaning the raw data:
        1. Extract raw data downloaded from Bloomberg/Refinitiv in Excel
        2. Transform data (convert wide format to long format)
        3. Load transformed data by exporting to Excel.
    """

    def __init__(self):
        super().__init__()

    def extract_data(self, file_name: str, sheet_name: str):
        return pd.read_excel(os.path.join(self.raw_data_root, file_name), sheet_name=sheet_name)

    def transform_data(self, data):
        return data

    @staticmethod
    def load_data(data, file_name: str, sheet_name: str):
        with pd.ExcelWriter(file_name) as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)


class BloombergESG(CleanBase):
    """
    Clean S&P Global (RobecoSAM) and Sustainalytics ESG data downloaded from Bloomberg.
    """

    def __init__(self):
        super().__init__()

    def control(self):
        data = self.extract_data(file_name=Variables.BloombergDB.RAW_DATA_FILE_NAME,
                                 sheet_name=Variables.BloombergDB.ESG_SHEET_NAME)
        data_t = self.transform_data(data)
        self.load_data(transformed_data=data_t,
                       file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.BLOOMBERG_ESG_SHEET_NAME)

    def transform_data(self, data):
        # fill BB_Ticker to missing places
        data.iloc[2, :] = data.iloc[2, :].fillna(method='ffill', axis=0)

        data = data.rename(columns=data.iloc[2])  # rename columns to BB_Tickers

        data = data.iloc[4:, :].reset_index(drop=True)  # remove redundant headers

        # reset index to 'Dates'
        data = data.rename(columns={data.columns[0]: 'Dates'})
        data = data.set_index('Dates')

        # reshape data (also drop NA values)
        temp = data.T
        temp = temp.set_index(['Dates'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={
            temp.columns[0]: Variables.BloombergDB.BB_TICKER,
            temp.columns[1]: 'variable'})

        data_t = temp.melt(id_vars=[Variables.BloombergDB.BB_TICKER, 'variable'], var_name='Dates')
        data_t = pd.pivot_table(
            data_t,
            values='value',
            index=[Variables.BloombergDB.BB_TICKER, 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        data_t = data_t.reset_index()
        data_t = data_t.rename(columns={
            data_t.columns[0]: Variables.BloombergDB.BB_TICKER,
            data_t.columns[1]: 'Dates'
        })

        # extract month and year from reported days
        # which will be used for merging data to run regression
        data_t['Dates'] = pd.to_datetime(data_t['Dates'])
        data_t['month'] = data_t['Dates'].dt.month
        data_t['year'] = data_t['Dates'].dt.year
        data_t['Dates'] = data_t['Dates'].dt.date

        # sort values by dates
        data_t = data_t.sort_values([Variables.BloombergDB.BB_TICKER, 'Dates'], ascending=True)

        return data_t


class RefinitivESG(CleanBase):
    """
    Clean ESG data downloaded from Refinitiv.
    """

    def __init__(self):
        super().__init__()

    def control(self):
        data = self.extract_data(file_name=Variables.RefinitivDB.RAW_DATA_FILE_NAME,
                                 sheet_name=Variables.RefinitivDB.ESG_SHEET_NAME)
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

        # shift Dates to 1 day backward to get end-of-month rating
        data_t['Dates'] = pd.to_datetime(data_t['Dates'])
        data_t['Dates'] = data_t['Dates'] - pd.Timedelta('1 day')

        # extract month and year from reported date
        data_t['month'] = data_t['Dates'].dt.month
        data_t['year'] = data_t['Dates'].dt.year
        data_t['Dates'] = data_t['Dates'].dt.date

        # sort values
        data_t = data_t.sort_values(['company_isin', 'Dates'], ascending=True)
        data_t = data_t.rename(columns={'company_isin': 'ID_ISIN'})

        # merge with 'company_info.xlsx' to get BB_TICKER
        data_t = data_t.merge(self.company_info[[Variables.BloombergDB.BB_TICKER, 'ID_ISIN']], on='ID_ISIN', how='outer')
        data_t = data_t.loc[data_t['Dates'].notnull()]

        # exclude data before 2006
        data_t = data_t.loc[data_t['Dates'] > date(2005, 12, 31)].reset_index(drop=True)

        # exclude data that are not in selected companies sample
        data_t = data_t.loc[data_t[Variables.BloombergDB.BB_TICKER].notnull()]

        return data_t


class BloombergCreditRtg(CleanBase):
    """
    This class clean and transform data for credit ratings.
    It performs the following steps:

        - clean_supervisor_data():
            + clean credit ratings provided by supervisor (Zorka)

        - clean_bb_data():
            + clean credit ratings changes downloaded from Bloomberg

        - merge_all():
            + merge the two above datasets

        - hard_code_rtg():
            + transform credit ratings to an ordinal scale

        - classify_rtg():
            + label whether a rating is investment / speculative grade

        - populate_rtg():
            + populate credit ratings to monthly data
            + because we only have information when there is a change in credit ratings from Bloomberg,
            not a continuous time series
    """

    def __init__(self):
        super().__init__()

    def control(self):
        """
        This function executes workflow of cleaning credit ratings
        """

        # get supervisor's provided data
        supervisor_data = self.extract_data(file_name=Variables.SupervisorData.FILE_NAME,
                                            sheet_name=Variables.SupervisorData.SHEET_NAME)

        # clean supervisor's provided data
        supervisor_data_c = self.clean_supervisor_data(supervisor_data)

        # get Bloomberg data
        bb_data = self.extract_data(file_name=Variables.BloombergDB.RAW_DATA_FILE_NAME,
                                    sheet_name=Variables.BloombergDB.SP_RATING_CHANGES_SHEET_NAME)

        # clean Bloomberg data
        bb_data_c = self.clean_bb_data(bb_data)

        # merge cleaned Bloomberg data and supervisor's provided data
        data = self.merge_all(supervisor_data_c, bb_data_c)

        # transform credit ratings to an ordinal scale
        data_t = self.hard_code_rtg(data)

        # classify credit ratings
        sp_credit_rtg = self.classify_rtg(data_t)

        # populate cleaned ratings to monthly data from 2006 --> 2020
        populated_rtg = self.populate_rtg(sp_credit_rtg)

        # write cleaned ratings to Excel
        self.load_data(transformed_data=sp_credit_rtg, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.SP_CREDIT_RTG_SHEET_NAME)

        # write populated cleaned ratings to Excel
        self.load_data(transformed_data=populated_rtg, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.POPULATED_SP_CREDIT_RTG_SHEET_NAME)


    def clean_supervisor_data(self, supervisor_data):
        """
        Transform credit rating dataset provided by supervisor.
        """

        # merge credit ratings (from Zorka) to list of selected companies on 'company_id'
        data = self.company_info[['companyid', Variables.BloombergDB.BB_TICKER]].merge(
            supervisor_data[['companyid', 'rating_date', 'rating']],
            on='companyid',
            how='left')

        # remove NAs
        data = data.loc[data['rating'].notnull()]

        # convert 'rating_date' from datetime to date
        data['rating_date'] = data['rating_date'].dt.date

        return data

    @staticmethod
    def clean_bb_data(bb_data):
        """
        Transform credit rating changes downloaded from Bloomberg
        """
        # extract only LT Local Issuer Rating
        bb_data = bb_data.loc[bb_data['Rating Type'] == Variables.SPCreditRtg.LT_LOCAL_ISSUER]

        # extract ratings after change
        bb_data[['rating', 'outlook']] = bb_data['Curr Rtg'].str.split(' ', 1, expand=True)
        bb_data = bb_data[['Date', 'rating', 'Security Name']]

        # rename columns
        bb_data.rename(columns={'Date': 'rating_date', 'Security Name': Variables.BloombergDB.BB_TICKER}, inplace=True)

        # convert 'rating_date' from datetime to date
        bb_data['rating_date'] = pd.to_datetime(bb_data['rating_date']).dt.date

        return bb_data

    @staticmethod
    def merge_all(supervisor_data_c, bb_data_c):
        """
        Merge cleaned Bloomberg data and supervisor's provided data
            - Bloomberg data: timerange from 2006 --> 2020
            - Supervisor's data: timerange from 1980 --> 2015
                --> an outer merge is performed and then duplicates are dropped.
        """
        # merge
        data = supervisor_data_c.merge(bb_data_c,
                                       how='outer',
                                       on=[Variables.BloombergDB.BB_TICKER, 'rating_date', 'rating'])

        data = data.sort_values([Variables.BloombergDB.BB_TICKER, 'rating_date'], ascending=True)

        # drop duplicates and unnecessary column
        data = data.drop(columns=['companyid'])
        data = data.drop_duplicates(keep='first')

        return data

    @staticmethod
    def hard_code_rtg(data):
        """
        Transform credit rating to an ordinal scale
            - NR: rating has not been assigned or is no longer assigned.
        """
        data.loc[data['rating'] == 'NR', 'ordinal_rating'] = 0
        data.loc[data['rating'] == 'D', 'ordinal_rating'] = 1
        data.loc[data['rating'] == 'SD', 'ordinal_rating'] = 1
        data.loc[data['rating'] == 'C', 'ordinal_rating'] = 2
        data.loc[data['rating'] == 'CC', 'ordinal_rating'] = 3
        data.loc[data['rating'] == 'CCC-', 'ordinal_rating'] = 4
        data.loc[data['rating'] == 'CCC', 'ordinal_rating'] = 5
        data.loc[data['rating'] == 'CCC+', 'ordinal_rating'] = 6
        data.loc[data['rating'] == 'B-', 'ordinal_rating'] = 7
        data.loc[data['rating'] == 'B', 'ordinal_rating'] = 8
        data.loc[data['rating'] == 'B+', 'ordinal_rating'] = 9
        data.loc[data['rating'] == 'BB-', 'ordinal_rating'] = 10
        data.loc[data['rating'] == 'BB', 'ordinal_rating'] = 11
        data.loc[data['rating'] == 'BB+', 'ordinal_rating'] = 12
        data.loc[data['rating'] == 'BBB-', 'ordinal_rating'] = 13
        data.loc[data['rating'] == 'BBB', 'ordinal_rating'] = 14
        data.loc[data['rating'] == 'BBB+', 'ordinal_rating'] = 15
        data.loc[data['rating'] == 'A-', 'ordinal_rating'] = 16
        data.loc[data['rating'] == 'A', 'ordinal_rating'] = 17
        data.loc[data['rating'] == 'A+', 'ordinal_rating'] = 18
        data.loc[data['rating'] == 'AA-', 'ordinal_rating'] = 19
        data.loc[data['rating'] == 'AA', 'ordinal_rating'] = 20
        data.loc[data['rating'] == 'AA+', 'ordinal_rating'] = 21
        data.loc[data['rating'] == 'AAA', 'ordinal_rating'] = 22

        return data

    @staticmethod
    def classify_rtg(data):
        """
        Labels grade to credit ratings
            - if > 12 (i.e. BB+): grade = 'investment'
            - else: grade = 'speculative'
        """
        data.loc[data['ordinal_rating'] > 12, 'grade'] = 'investment'
        data.loc[data['ordinal_rating'] <= 12, 'grade'] = 'speculative'

        return data

    @staticmethod
    def populate_rtg(data):
        """
        Populate credit ratings to monthly data from 2006 - 2020
        by using 'ffill' method from pandas package.
        """

        # extract month and year from rating_date
        data['rating_date'] = pd.to_datetime(data['rating_date'])
        data['month'] = data['rating_date'].dt.month
        data['year'] = data['rating_date'].dt.year

        series = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

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
        for company in rating[Variables.BloombergDB.BB_TICKER].unique():
            df = rating.loc[rating[Variables.BloombergDB.BB_TICKER] == company]
            df = series.merge(df, on=['month', 'year'], how='outer')
            df = df.fillna(method='ffill')  # propagate last valid observation forward to next valid
            populated_rtg.append(df)
        populated_rtg = pd.concat(populated_rtg)

        # only get data between 2006 and 2020
        populated_rtg = populated_rtg.loc[(populated_rtg['year'] >= 2006) & (populated_rtg['year'] <= 2020)]

        # drop NA values
        populated_rtg = populated_rtg.dropna(axis=0, how='any')

        return populated_rtg


class BloombergAccounting(BloombergESG):

    def __init__(self):
        super().__init__()

    def control(self):
        data = self.extract_data(file_name=Variables.BloombergDB.RAW_DATA_FILE_NAME,
                                 sheet_name=Variables.BloombergDB.ACCOUNTING_SHEET_NAME)
        data_t = self.transform_data(data)
        self.load_data(transformed_data=data_t, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.ACCOUNTING_SHEET_NAME)

        data = self.calculate_control_var(data_t)
        populated_data = self.populate(data)
        self.load_data(transformed_data=populated_data, file_name=Variables.CleanedData.FILE_NAME,
                       sheet_name=Variables.CleanedData.POPULATED_ACCOUNTING_SHEET_NAME)

    @staticmethod
    def calculate_control_var(data):
        """
        Calculate additional control variables
            - SIZE = natural log of Total Assets in millions of Euros
            - LEVERAGE = (Long-term Borrowing / Total Assets) * 100
            - ROA = (EBIT / Total Assets) * 100
        """
        data['SIZE'] = np.log(data['BS_TOT_ASSET'])
        data['LEVERAGE'] = (data['BS_LT_BORROW'] / data['BS_TOT_ASSET']) * 100

        return data

    @staticmethod
    def populate(data):
        """
        Populate accounting data to monthly data from 2006 - 2020.
        """
        series = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))
        data = data[[
            Variables.BloombergDB.BB_TICKER,
            'month',
            'year',
            Variables.ControlVar.LEV,
            Variables.ControlVar.SIZE,
            Variables.ControlVar.ICOV,
            Variables.ControlVar.OMAR,
        ]]
        populated = []
        for company in data[Variables.BloombergDB.BB_TICKER].unique():
            df = data.loc[data[Variables.BloombergDB.BB_TICKER] == company]
            min_year = min(df['year'])
            max_year = max(df['year'])
            df = series.merge(df, on=['month', 'year'], how='left')
            df = df.fillna(method='bfill')  # use next valid observation to fill gap
            df = df.loc[(df['year'] >= min_year) & (df['year'] <= max_year)]
            populated.append(df)
        populated = pd.concat(populated)

        # drop row having NA values
        populated = populated.dropna(axis=0, how='any')

        return populated


if __name__ == "__main__":
    # BloombergESG().control()
    # RefinitivESG().control()
    # BloombergCreditRtg().control()
    # BloombergAccounting().control()
    pass
