import os
from datetime import date

import pandas as pd


class DataRoot:

    def __init__(self):

        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.raw_data_root = os.path.join(self.project_root, 'data', 'raw_data')
        self.cleaned_data_root = os.path.join(self.project_root, 'data', 'cleaned_data')

    def extract_esg_data(self, file_name: str, sheet_name: str):
        """
        Get ESG data downloaded from data sources (Bloomberg/Refinitiv) in raw format.
        """
        return pd.read_excel(os.path.join(self.raw_data_root, file_name), sheet_name=sheet_name)

    def transform_esg_data(self, data):
        """
        Transform raw data from wide to long format.
        """
        return data

    @staticmethod
    def load_esg_data(transformed_data, file_name: str, sheet_name: str):
        """
        Export transformed data to Excel.
        """
        with pd.ExcelWriter(file_name) as writer:
            transformed_data.to_excel(writer, sheet_name=sheet_name, index=False)



class BloombergData(DataRoot):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        esg_bb = self.extract_esg_data(file_name='raw_data_bloomberg.xlsx', sheet_name='ESG SCORE')
        transformed_esg_bb = self.transform_esg_data(esg_bb)
        self.load_esg_data(transformed_data=transformed_esg_bb,
                           file_name='cleaned_bb_esg_data.xlsx',
                           sheet_name='ESG_BLOOMBERG')


    def transform_esg_data(self, esg_bb):
        """
        Transform ESG data from wide to long format.
        """

        # fill fundamental ticker to missing places
        esg_bb.iloc[2, :] = esg_bb.iloc[2, :].fillna(method='ffill', axis=0)

        # rename columns
        esg_bb = esg_bb.rename(columns=esg_bb.iloc[2])

        # remove redundant headers
        esg_bb = esg_bb.iloc[4:, :]
        esg_bb = esg_bb.reset_index(drop=True)

        # reset index
        esg_bb = esg_bb.rename(columns={esg_bb.columns[0]: 'Dates'})
        esg_bb = esg_bb.set_index('Dates')

        # reshape data (also drop NA values)
        temp = esg_bb.T
        temp = temp.set_index(['Dates'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={temp.columns[0]: 'company_name', temp.columns[1]: 'variable'})

        data = temp.melt(id_vars=['company_name', 'variable'], var_name='Dates')
        data = pd.pivot_table(data,
                              values='value',
                              index=['company_name', 'Dates'],
                              columns=['variable'],
                              aggfunc='first')
        data = data.reset_index()
        data = data.rename(columns={data.columns[0]: 'company_name', data.columns[1]: 'Dates'})
        data['Dates'] = pd.to_datetime(data['Dates'])
        data['Dates'] = data['Dates'].dt.date

        # sort values
        data = data.sort_values(['company_name', 'Dates'], ascending=True)

        return data


class RefinitivData(DataRoot):

    def __init__(self):
        super().__init__()

    def control(self):
        """
        ETL Process
        """
        esg_ek = self.extract_esg_data(file_name='raw_data_refinitiv.xlsx', sheet_name='ESG Score')
        transformed_esg_ek = self.transform_esg_data(esg_ek)
        self.load_esg_data(transformed_data=transformed_esg_ek,
                           file_name='cleaned_refinitiv_esg_data.xlsx',
                           sheet_name='ESG_REFINITIV')

    def transform_esg_data(self, esg_ek):
        # set index
        esg_ek = esg_ek.set_index('Name')

        # rename columns and esg variables
        df = esg_ek.iloc[0, :]
        df = df.reset_index(drop=True)
        # df = df.iloc[1:]
        df = df.to_frame()
        df = df.assign(list=df['Code'].str.split("(")).explode("list")
        df = df.reset_index(drop=True)
        column_names = df["list"].iloc[::2]  # extract even indexes
        variable_names = df["list"].iloc[1::2]  # extract odd indexes

        esg_ek.columns = list(column_names)
        esg_ek.loc["Code", :] = list(variable_names)

        # rename index to 'Dates'
        esg_ek = esg_ek.reset_index()
        esg_ek = esg_ek.rename(columns={esg_ek.columns[0]: 'Dates'})
        esg_ek = esg_ek.set_index('Dates')

        # reshape data (also drop NA values)
        temp = esg_ek.T
        temp = temp.set_index(['Code'], append=True)
        temp = temp.reset_index()
        temp = temp.rename(columns={temp.columns[0]: 'company_isin', temp.columns[1]: 'variable'})

        data = temp.melt(id_vars=['company_isin', 'variable'], var_name='Dates')
        data = pd.pivot_table(data,
                              values='value',
                              index=['company_isin', 'Dates'],
                              columns=['variable'],
                              aggfunc='first')
        data = data.reset_index()
        data['Dates'] = pd.to_datetime(data['Dates'])
        data['Dates'] = data['Dates'].dt.date

        # sort values
        data = data.sort_values(['company_isin', 'Dates'], ascending=True)

        # merge with 'company_info.xlsx' to get company equity ticker
        company_info = pd.read_excel(os.path.join(self.raw_data_root, 'company_info.xlsx'), sheet_name='company_info')
        company_info = company_info[["Fundamental Ticker Equity", "ID_ISIN"]]

        data = data.rename(columns={'company_isin': 'ID_ISIN'})

        data = data.merge(company_info, on='ID_ISIN', how='outer')
        data = data.loc[data['Dates'].notnull()]

        # shift Dates to 1 day backward to get end-of-month rating
        data['Dates'] = data['Dates'] - pd.Timedelta('1 day')

        # exclude data before 2006
        data = data.loc[data['Dates'] > date(2005, 12, 31)].reset_index(drop=True)

        data = data.loc[data['Fundamental Ticker Equity'].notnull()]

        return data


# BloombergData().control()
# RefinitivData().control()
