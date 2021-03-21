import os
from datetime import date

import pandas as pd
import numpy as np

from lib.variable_names import VariableNames


class CleanBase:

    def __init__(self):

        # data path
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.raw_data_root = os.path.join(self.project_root, 'data', 'raw_data')
        self.cleaned_data_root = os.path.join(self.project_root, 'data', 'cleaned_data')

        # overall company info
        self.company_info = pd.read_excel(os.path.join(self.raw_data_root, VariableNames.Bloomberg.FILE_NAME),
                                          sheet_name=VariableNames.Bloomberg.COMPANY_INFO_SHEET_NAME)

    def extract_data(self, file_name: str, sheet_name: str):
        """
        Get raw data downloaded from data sources (Bloomberg/Refinitiv).
        """
        return pd.read_excel(os.path.join(self.raw_data_root, file_name), sheet_name=sheet_name)

    def transform_data(self, data):
        """
        Transform raw data from wide to long format.
        """
        return data

    @staticmethod
    def load_data(data, file_name: str, sheet_name: str):
        """
        Export transformed data to Excel.
        """
        with pd.ExcelWriter(file_name) as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)


class BloombergESG(CleanBase):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        data = self.extract_data(file_name=VariableNames.Bloomberg.FILE_NAME,
                                 sheet_name=VariableNames.Bloomberg.ESG_SHEET_NAME)
        transformed_data = self.transform_data(data)
        self.load_data(transformed_data=transformed_data,
                       file_name=VariableNames.CleanedData.FILE_NAME,
                       sheet_name=VariableNames.CleanedData.BLOOMBERG_ESG_SHEET_NAME)

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
            temp.columns[0]: VariableNames.Bloomberg.BB_TICKER,
            temp.columns[1]: 'variable'})

        transformed_data = temp.melt(id_vars=[VariableNames.Bloomberg.BB_TICKER, 'variable'], var_name='Dates')
        transformed_data = pd.pivot_table(
            transformed_data,
            values='value',
            index=[VariableNames.Bloomberg.BB_TICKER, 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        transformed_data = transformed_data.reset_index()
        transformed_data = transformed_data.rename(columns={
            transformed_data.columns[0]: VariableNames.Bloomberg.BB_TICKER,
            transformed_data.columns[1]: 'Dates'
        })

        # extract month and year from reported days
        # which will be used for merging data to run regression
        transformed_data['Dates'] = pd.to_datetime(transformed_data['Dates'])
        transformed_data['month'] = transformed_data['Dates'].dt.month
        transformed_data['year'] = transformed_data['Dates'].dt.year
        transformed_data['Dates'] = transformed_data['Dates'].dt.date

        # sort values
        transformed_data = transformed_data.sort_values([VariableNames.Bloomberg.BB_TICKER, 'Dates'], ascending=True)

        return transformed_data


class RefinitivESG(CleanBase):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        data = self.extract_data(file_name=VariableNames.Refinitiv.FILE_NAME,
                                 sheet_name=VariableNames.Refinitiv.ESG_SHEET_NAME)
        transformed_data = self.transform_data(data)
        self.load_data(transformed_data=transformed_data,
                       file_name=VariableNames.CleanedData.FILE_NAME,
                       sheet_name=VariableNames.CleanedData.REFINITIV_ESG_SHEET_NAME)

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

        transformed_data = temp.melt(id_vars=['company_isin', 'variable'], var_name='Dates')
        transformed_data = pd.pivot_table(
            transformed_data,
            values='value',
            index=['company_isin', 'Dates'],
            columns=['variable'],
            aggfunc='first'
        )
        transformed_data = transformed_data.reset_index()

        # extract month and year from reported date
        transformed_data['Dates'] = pd.to_datetime(transformed_data['Dates'])
        transformed_data['month'] = transformed_data['Dates'].dt.month
        transformed_data['year'] = transformed_data['Dates'].dt.year
        transformed_data['Dates'] = transformed_data['Dates'].dt.date

        # sort values
        transformed_data = transformed_data.sort_values(['company_isin', 'Dates'], ascending=True)
        transformed_data = transformed_data.rename(columns={'company_isin': 'ID_ISIN'})

        # merge with 'company_info.xlsx' to get BB_TICKER
        transformed_data = transformed_data.merge(self.company_info[[VariableNames.Bloomberg.BB_TICKER, 'ID_ISIN']],
                                                  on='ID_ISIN',
                                                  how='outer')
        transformed_data = transformed_data.loc[transformed_data['Dates'].notnull()]

        # shift Dates to 1 day backward to get end-of-month rating
        transformed_data['Dates'] = transformed_data['Dates'] - pd.Timedelta('1 day')

        # exclude data before 2006
        transformed_data = transformed_data.loc[transformed_data['Dates'] > date(2005, 12, 31)].reset_index(drop=True)

        # exclude data that are not in selected companies
        transformed_data = transformed_data.loc[transformed_data[VariableNames.Bloomberg.BB_TICKER].notnull()]

        return transformed_data


class BloombergCreditRtg(CleanBase):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        rating_zorka = self.extract_data(file_name='credit_rating_Zorka.xlsx', sheet_name='credit_rating_Zorka')

        transformed = self.transform_data(rating_zorka)
        result = self.hard_code_rating(transformed)
        self.load_data(transformed_data=result,
                       file_name='cleaned_credit_rating.xlsx',
                       sheet_name='SP_credit_rating')

        populated_rating = self.fill_rating(result)
        self.load_data(transformed_data=populated_rating,
                       file_name='cleaned_credit_rating.xlsx',
                       sheet_name='populated_SP_credit_rating')

    def transform_data(self, rating_zorka):
        company_info = self.extract_data(file_name='company_info.xlsx', sheet_name='company_info')

        ##################################
        # transform data provided by Zorka
        ##################################


        # merge credit ratings (from Zorka) to selected companies
        data = company_info[['companyid', 'Fundamental Ticker Equity']].merge(
            rating_zorka[['companyid', 'rating_date', 'rating']],
            on='companyid',
            how='left'
        )

        # remove NA
        data = data.loc[data['rating'].notnull()]
        data['rating_date'] = data['rating_date'].dt.date

        ###############################
        # transform data from Bloomberg
        ###############################

        # get rating changes from Bloomberg
        rating_changes_bb = self.extract_data(file_name='raw_data_bloomberg_credit_rating.xlsx',
                                              sheet_name='Rating Changes S&P')

        # only get LT Foreign Rating
        rating_changes_bb = rating_changes_bb.loc[rating_changes_bb['Rating Type'] == 'LT Foreign Issuer Credit']

        # retrieve current rating
        rating_changes_bb = rating_changes_bb[['Date', 'Curr Rtg', 'Security Name']]
        rating_changes_bb[['rating', 'outlook']] = rating_changes_bb['Curr Rtg'].str.split(' ', 1, expand=True)
        rating_changes_bb = rating_changes_bb.drop(columns=['Curr Rtg', 'outlook'])

        rating_changes_bb['Date'] = pd.to_datetime(rating_changes_bb['Date'])
        rating_changes_bb['Date'] = rating_changes_bb['Date'].dt.date

        rating_changes_bb = rating_changes_bb.rename(columns={'Date': 'rating_date',
                                                              'Security Name': 'Fundamental Ticker Equity'})

        ###################################
        # merge data from Zorka & Bloomberg
        ###################################
        result = data.merge(rating_changes_bb, how='outer', on=['Fundamental Ticker Equity', 'rating_date', 'rating'])
        result = result.sort_values(['Fundamental Ticker Equity', 'rating_date'], ascending=True)

        result = result.drop(columns=['companyid'])
        result = result.drop_duplicates(keep='first')

        return result

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
    def fill_rating(data):
        """
        Populate credit ratings to monthly data from 2006 - 2020
        """

        # data['rating_date'] = data['rating_date'].dt.date
        data['rating_date'] = pd.to_datetime(data['rating_date'])

        # extract month and year from rating_date
        data['rating_month'] = data['rating_date'].dt.month
        data['rating_year'] = data['rating_date'].dt.year

        # generate list of month and year from 2006 to 2020
        daterange = pd.date_range(start=date(2006, 1, 1), end=date(2020, 12, 31), freq='1M').to_frame()
        daterange['rating_month'] = daterange[0].dt.month
        daterange['rating_year'] = daterange[0].dt.year
        daterange = daterange[['rating_month', 'rating_year']].reset_index(drop=True)

        ########################
        # populate credit rating
        ########################

        rating = data[['Fundamental Ticker Equity', 'ordinal_rating', 'rating_month', 'rating_year']]

        # drop duplicated rating
        # there are cases when companies have credit rating changes more than one time within a month
        # but these cases are very rare, and thus we only keep the latest value within that month
        rating = rating.drop_duplicates(keep='last')

        # populate (this also excludes data after 2020)
        populated_rating = []
        for company in rating['Fundamental Ticker Equity'].unique():
            df = rating.loc[rating['Fundamental Ticker Equity'] == company]
            df = daterange.merge(df, on=['rating_month', 'rating_year'], how='outer')
            df = df.fillna(method='ffill')  # propagate last valid observation forward to next valid
            populated_rating.append(df)
        populated_rating = pd.concat(populated_rating)

        # only get data between 2006 and 2020
        populated_rating = populated_rating.loc[(populated_rating['rating_year'] >= 2006) &
                                                (populated_rating['rating_year'] <= 2020)]

        # drop NA values
        populated_rating = populated_rating.dropna(axis=0, how='any')

        return populated_rating


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
    RefinitivESG().control()
    # CreditRating().control()
    # AccountingData().control()
    pass
