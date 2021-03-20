import os
import pandas as pd

from lib.clean_data import BaseClass


# ToDo make a class of variable names


class AnalyseData(BaseClass):

    def __init__(self):
        super().__init__()

    def control(self):
        cleaned_data_dict = self.extract_cleaned_data()
        esg_availability = self.check_data_availability(cleaned_data_dict)
        self.check_time_range_esg(cleaned_data_dict, esg_availability)

    def extract_cleaned_data(self):
        """
        Return a dictionary contains (cleaned) ESG ratings and credit ratings of each provider.
            - Sustainalytics: ESG rating
            - RobecoSAM (S&P Global): ESG rating
            - Refinitiv: ESG rating
            - S&P: credit rating
        """

        # get companies with Sustainalytics ESG ratings
        esg_bb = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'), sheet_name='ESG_BLOOMBERG')
        esg_bb = esg_bb.rename(columns={'company_name': 'Fundamental Ticker Equity'})
        sustainalytics = esg_bb.loc[esg_bb['SUSTAINALYTICS_RANK'].notnull()]
        sustainalytics['sustainalytics_rating'] = True

        # get companies with RobecoSAM ESG ratings
        robecosam = esg_bb.loc[esg_bb['ROBECOSAM_TOTAL_STBLY_RANK'].notnull()]
        robecosam['robecosam_rating'] = True

        # get companies with Refinitiv ESG ratings
        refinitiv = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'), sheet_name='ESG_REFINITIV')
        refinitiv['refinitiv_rating'] = True

        # get companies with S&P credit rating
        sp = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'), sheet_name='SP_credit_rating')
        sp['sp_rating'] = True

        # get companies with populated S&P credit rating
        populated_sp = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'),
                                     sheet_name='populated_SP_credit_rating')

        return {'robecosam': robecosam,
                'sustainalytics': sustainalytics,
                'refinitiv': refinitiv,
                'sp': sp,
                'populated_sp': populated_sp}

    def check_data_availability(self, cleaned_data_dict):
        """
        Return companies with:
            - at least 1 ESG rating ('esg_data' = True)
            - no ESG rating ('esg_data' = False).
            - credit rating (credit_rating = True, otherwise False)
        """
        # get list of companies
        company_list = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'),
                                     sheet_name='company_info')
        company_list = company_list[['Fundamental Ticker Equity']]

        # get sustainalytics esg rating availability
        sustainalytics_short = company_list.merge(
            cleaned_data_dict['sustainalytics'][['Fundamental Ticker Equity', 'sustainalytics_rating']],
            on='Fundamental Ticker Equity',
            how='left'
        )
        sustainalytics_short = sustainalytics_short.drop_duplicates(keep='first').reset_index(drop=True)

        # get robecosam esg rating availability
        robecosam_short = company_list.merge(
            cleaned_data_dict['robecosam'][['Fundamental Ticker Equity', 'robecosam_rating']],
            on='Fundamental Ticker Equity',
            how='left'
        )
        robecosam_short = robecosam_short.drop_duplicates(keep='first').reset_index(drop=True)

        # get refinitiv esg rating availability
        refinitiv_short = company_list.merge(
            cleaned_data_dict['refinitiv'][['Fundamental Ticker Equity', 'refinitiv_rating']],
            on='Fundamental Ticker Equity',
            how='left'
        )
        refinitiv_short = refinitiv_short.drop_duplicates(keep='first').reset_index(drop=True)

        # get S&P credit rating availability
        sp_short = company_list.merge(
            cleaned_data_dict['sp'][['Fundamental Ticker Equity', 'sp_rating']],
            on='Fundamental Ticker Equity',
            how='left'
        )
        sp_short = sp_short.drop_duplicates(keep='first').reset_index(drop=True)

        # merge all data
        result = sustainalytics_short.merge(robecosam_short, how='outer', on='Fundamental Ticker Equity')
        result = result.merge(refinitiv_short, how='outer', on='Fundamental Ticker Equity')
        result = result.merge(sp_short, how='outer', on='Fundamental Ticker Equity')

        result.loc[
            (result['refinitiv_rating'].isnull()) &
            (result['robecosam_rating'].isnull()) &
            (result['sustainalytics_rating'].isnull()),
            'esg_data'
        ] = False

        result.loc[
            (result['refinitiv_rating'].notnull()) |
            (result['robecosam_rating'].notnull()) |
            (result['sustainalytics_rating'].notnull()),
            'esg_data'
        ] = True

        # check whether companies can be used to analyzed
        # 'analyze' = True if 'sp_rating' = True
        # 'analyze' = False if 'sp_rating' = False
        result.loc[result['sp_rating'].isnull(), 'analyze'] = False
        result.loc[result['sp_rating'].notnull(), 'analyze'] = True

        return result

    @staticmethod
    def check_time_range_esg(esg_dict, esg_availability):
        """
        Return first and last available date of esg ratings.
        """

        # extract time range of sustainalytics rating
        for company in esg_dict['sustainalytics']['Fundamental Ticker Equity'].unique():
            temp = esg_dict['sustainalytics'].loc[esg_dict['sustainalytics']['Fundamental Ticker Equity'] == company]
            temp = temp.sort_values(by='Dates')
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'first_sustainalytics_date'
            ] = list(temp['Dates'])[0]
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'last_sustainalytics_date'
            ] = list(temp['Dates'])[-1]

        # extract time range of robecosam rating
        for company in esg_dict['robecosam']['Fundamental Ticker Equity'].unique():
            temp = esg_dict['robecosam'].loc[esg_dict['robecosam']['Fundamental Ticker Equity'] == company]
            temp = temp.sort_values(by='Dates')
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'first_robecosam_date'
            ] = list(temp['Dates'])[0]
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'last_robecosam_date'
            ] = list(temp['Dates'])[-1]

        # extract time range of refinitiv rating
        for company in esg_dict['refinitiv']['Fundamental Ticker Equity'].unique():
            temp = esg_dict['refinitiv'].loc[esg_dict['refinitiv']['Fundamental Ticker Equity'] == company]
            temp = temp.sort_values(by='Dates')
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'first_refinitiv_date'
            ] = list(temp['Dates'])[0]
            esg_availability.loc[
                esg_availability['Fundamental Ticker Equity'] == company,
                'last_refinitiv_date'
            ] = list(temp['Dates'])[-1]

        # convert datetime to date
        esg_availability['first_sustainalytics_date'] = pd.to_datetime(
            esg_availability['first_sustainalytics_date']).dt.date
        esg_availability['last_sustainalytics_date'] = pd.to_datetime(
            esg_availability['last_sustainalytics_date']).dt.date
        esg_availability['first_robecosam_date'] = pd.to_datetime(esg_availability['first_robecosam_date']).dt.date
        esg_availability['last_robecosam_date'] = pd.to_datetime(esg_availability['last_robecosam_date']).dt.date
        esg_availability['first_refinitiv_date'] = pd.to_datetime(esg_availability['first_refinitiv_date']).dt.date
        esg_availability['last_refinitiv_date'] = pd.to_datetime(esg_availability['last_refinitiv_date']).dt.date

        return esg_availability

    @staticmethod
    def descriptive_statistics(cleaned_data_dict: dict, provider: str):
        """
        Return a dataframe of descriptive statistics for a rating provider year by year.
        *arg
            provider: choices are 'refinitiv' / 'robecosam' / 'sustainalytics' / 'sp'
        """

        score_name = ''
        if provider == 'refinitiv':
            score_name = 'TRESGS'
        elif provider == 'robecosam':
            score_name = 'ROBECOSAM_TOTAL_STBLY_RANK'
        elif provider == 'sustainalytics':
            score_name = 'SUSTAINALYTICS_RANK'
        elif provider == 'sp':
            score_name = 'ordinal_rating'

        data = cleaned_data_dict[provider]
        data['year'] = data['Dates'].dt.year

        # get descriptive statistics by year
        result = pd.DataFrame()
        for year in data['year'].unique():
            data_by_year = data.loc[data['year'] == year]
            temp = pd.DataFrame(data_by_year[score_name].describe()).T
            temp['skewness'] = data_by_year[score_name].skew()
            temp['kurtosis'] = data_by_year[score_name].kurtosis()
            temp['year'] = year
            temp['no_companies'] = len(data_by_year['Fundamental Ticker Equity'].unique())
            result = result.append(temp, ignore_index=True)
        result = result.sort_values(by='year')
        result = result.round(decimals=2)
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


AnalyseData().control()
