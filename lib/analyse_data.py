import os
import pandas as pd

from lib.clean_data import DataRoot


class AnalyseData(DataRoot):

    def __init__(self):
        super().__init__()

    def check_availability_esg_data(self):
        esg_bb = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'), sheet_name='ESG_BLOOMBERG')
        esg_bb = esg_bb.rename(columns={'company_name': 'Fundamental Ticker Equity'})

        # get list of companies
        company_list = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'),
                                     sheet_name='company_info')
        company_list = company_list[['Fundamental Ticker Equity']]

        # get companies with Sustainalytics ratings
        sustainalytics = esg_bb.loc[esg_bb['SUSTAINALYTICS_RANK'].notnull()]
        sustainalytics['sustainalytics_rating'] = True
        sustainalytics = company_list.merge(sustainalytics[['Fundamental Ticker Equity', 'sustainalytics_rating']],
                                            on='Fundamental Ticker Equity',
                                            how='left')
        sustainalytics = sustainalytics.drop_duplicates(keep='first').reset_index(drop=True)

        # get companies with RobecoSAM ratings
        robecosam = esg_bb.loc[esg_bb['ROBECOSAM_TOTAL_STBLY_RANK'].notnull()]
        robecosam['robecosam_rating'] = True
        robecosam = company_list.merge(robecosam[['Fundamental Ticker Equity', 'robecosam_rating']],
                                       on='Fundamental Ticker Equity',
                                       how='left')
        robecosam = robecosam.drop_duplicates(keep='first').reset_index(drop=True)

        # get companies with Refinitiv ratings
        refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'), sheet_name='ESG_REFINITIV')
        refinitiv['refinitiv_rating'] = True
        refinitiv = company_list.merge(refinitiv[['Fundamental Ticker Equity', 'refinitiv_rating']],
                                       on='Fundamental Ticker Equity',
                                       how='left')
        refinitiv = refinitiv.drop_duplicates(keep='first').reset_index(drop=True)

        # merge all data
        result = sustainalytics.merge(robecosam, how='outer', on='Fundamental Ticker Equity')
        result = result.merge(refinitiv, how='outer', on='Fundamental Ticker Equity')

        # self.load_esg_data(result, file_name='\\esg_data_availability.xlsx', sheet_name='esg_data_availability')
        with pd.ExcelWriter(os.path.join(self.cleaned_data_root, 'output.xlsx')) as writer:
            result.to_excel(writer, sheet_name='esg_data_availability')

        return result


class Helper:

    @staticmethod
    def check_availability_esg_data():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data', 'uyen\'s data')

        data = pd.read_excel(os.path.join(data_root, 'cleaned_data.xlsx'), sheet_name='esg_data_bb')
        len(data.companyname.unique())

        # get companies with SUSTAINALYTICS' data
        sustainalytics = data.loc[data['SUSTAINALYTICS_RANK'].notnull()]
        len(sustainalytics.companyname.unique())

        # get company with RobecoSAM data
        robecosam = data.loc[data['ROBECOSAM_TOTAL_STBLY_RANK'].notnull()]
        len(robecosam.companyname.unique())

        company_list = pd.read_excel(os.path.join(data_root, 'company_list_final.xlsx'),
                                     sheet_name='general_data_info')
        company_list_simple = company_list[['companyname',
                                            'bloomberg_fundamental_ticker',
                                            'esg_sustainalytics',
                                            'esg_robecosam']]

        for company in sustainalytics['companyname'].unique():
            temp = sustainalytics.loc[sustainalytics['companyname'] == company]
            temp = temp.sort_values(by='Dates')
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'first_esg_sustainalytics_date'
            ] = list(temp['Dates'])[0]
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'last_esg_sustainalytics_date'
            ] = list(temp['Dates'])[-1]

        for company in robecosam['companyname'].unique():
            temp = robecosam.loc[robecosam['companyname'] == company]
            temp = temp.sort_values(by='Dates')
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'first_esg_robecosam_date'
            ] = list(temp['Dates'])[0]
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'last_esg_robecosam_date'
            ] = list(temp['Dates'])[-1]

        company_list = company_list.merge(
            company_list_simple[['bloomberg_fundamental_ticker',
                                 'first_esg_sustainalytics_date',
                                 'last_esg_sustainalytics_date',
                                 'first_esg_robecosam_date',
                                 'last_esg_robecosam_date',
                                 ]],
            on='bloomberg_fundamental_ticker',
            how='outer'
        )

        company_list['first_credit_rating_date'] = pd.to_datetime(company_list['first_credit_rating_date'])
        company_list['last_credit_rating_date'] = pd.to_datetime(company_list['last_credit_rating_date'])
        company_list['first_esg_sustainalytics_date'] = pd.to_datetime(company_list['first_esg_sustainalytics_date'])
        company_list['last_esg_sustainalytics_date'] = pd.to_datetime(company_list['last_esg_sustainalytics_date'])
        company_list['first_esg_robecosam_date'] = pd.to_datetime(company_list['first_esg_robecosam_date'])
        company_list['last_esg_robecosam_date'] = pd.to_datetime(company_list['last_esg_robecosam_date'])

        company_list['first_credit_rating_date'] = company_list['first_credit_rating_date'].dt.date
        company_list['last_credit_rating_date'] = company_list['last_credit_rating_date'].dt.date
        company_list['first_esg_sustainalytics_date'] = company_list['first_esg_sustainalytics_date'].dt.date
        company_list['last_esg_sustainalytics_date'] = company_list['last_esg_sustainalytics_date'].dt.date
        company_list['first_esg_robecosam_date'] = company_list['first_esg_robecosam_date'].dt.date
        company_list['last_esg_robecosam_date'] = company_list['last_esg_robecosam_date'].dt.date

        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            company_list.to_excel(writer, sheet_name='company_downloaded', index=False)

    @staticmethod
    def check_availability_accounting_data_bb():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data', 'uyen\'s data')

        # get accounting data
        data = pd.read_excel(os.path.join(data_root, 'cleaned_data.xlsx'),
                             sheet_name='accounting_data_bb')
        data = data[['companyname', 'Dates', 'CUR_MKT_CAP']]

        # get company list
        company_list = pd.read_excel(os.path.join(data_root, 'company_list_final.xlsx'),
                                     sheet_name='general_data_info')
        company_list_simple = company_list[['companyname',
                                            'bloomberg_fundamental_ticker']]

        # merge data
        for company in data['companyname'].unique():
            temp = data.loc[data['companyname'] == company]
            temp = temp.sort_values(by='Dates')
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'first_accounting_data_date'
            ] = list(temp['Dates'])[0]
            company_list_simple.loc[
                company_list_simple['bloomberg_fundamental_ticker'] == company,
                'last_accounting_data_date'
            ] = list(temp['Dates'])[-1]

        company_list = company_list.merge(
            company_list_simple[['bloomberg_fundamental_ticker',
                                 'first_accounting_data_date',
                                 'last_accounting_data_date']],
            on='bloomberg_fundamental_ticker',
            how='outer'
        )

        # export data
        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            company_list.to_excel(writer, sheet_name='company_downloaded', index=False)

    @staticmethod
    def check_availability_to_analyse():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data', 'uyen\'s data')

        # get accounting data
        data = pd.read_excel(os.path.join(data_root, 'company_list_final.xlsx'),
                             sheet_name='general_data_info')

        # check dates
        data.loc[
            (
                    (data['first_esg_sustainalytics_date'] >= data['first_credit_rating_date']) &
                    (data['first_esg_sustainalytics_date'] >= data['first_accounting_data_date'])
            ) |
            (
                    (data['first_esg_robecosam_date'] >= data['first_credit_rating_date']) &
                    (data['first_esg_robecosam_date'] >= data['first_accounting_data_date'])
            ),
            'can be analyzed?'
        ] = 'yes'

        data.loc[
            (
                    (data['first_esg_sustainalytics_date'] < data['first_credit_rating_date']) |
                    (data['first_esg_sustainalytics_date'] < data['first_accounting_data_date'])
            ) |
            (
                    (data['first_esg_robecosam_date'] < data['first_credit_rating_date']) &
                    (data['first_esg_robecosam_date'] < data['first_accounting_data_date'])
            ),
            'can be analyzed?'
        ] = 'no'

        # export data
        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            data.to_excel(writer, sheet_name='company_downloaded', index=False)


AnalyseData().check_availability_esg_data()
