import os
import pandas as pd


class Helper:

    @staticmethod
    def get_credit_rating():
        """Credit rating is obtained from S&P, data provided by Zorka"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data', 'uyen\'s data')
        company_list = pd.read_excel(os.path.join(data_root, 'company_list.xlsx'),
                                     sheet_name='company_downloaded')
        company_list_simple = company_list[['companyname', 'org_id']]

        # get and clean credit rating from Zorka
        supervisor_data_root = os.path.join(project_root, 'data', 'supervisors\' data')
        credit_rating = pd.read_stata(os.path.join(supervisor_data_root, 'CorporateRatings_since_1980.dta'))

        # merge data
        # filter data from raw credit_rating based on company_list
        credit_rating = credit_rating[credit_rating['org_id'].isin(list(company_list_simple['org_id']))]
        # merge
        result = company_list_simple.merge(credit_rating, on='org_id', how='outer')

        # check if companyname is matching (status OK)
        result.loc[result['companyname_x'] == result['companyname_y'], 'check_name'] = 'equal'
        result.loc[result['companyname_x'] != result['companyname_y'], 'check_name'] = 'not equal'
        result['rating_date'] = result['rating_date'].dt.date
        # result.loc[result['check_name'] == ' not equal']

        # drop NA rating
        result = result.loc[result['rating'] != 'NR']

        # get credit rating information (first date, last date, count)
        for company in result['companyname_y'].unique():
            temp = result.loc[result['companyname_y'] == company]
            temp = temp.sort_values(by='rating_date')
            company_list_simple.loc[
                company_list_simple['companyname'] == company,
                'first_credit_rating_date'
            ] = list(temp['rating_date'])[0]
            company_list_simple.loc[
                company_list_simple['companyname'] == company,
                'last_credit_rating_date'
            ] = list(temp['rating_date'])[-1]
            company_list_simple.loc[
                company_list_simple['companyname'] == company,
                'time_credit_rating_changes'
            ] = len(temp['rating'])

        # export credit_rating data
        with pd.ExcelWriter('credit_rating' + '.xlsx') as writer:
            result.to_excel(writer, sheet_name='credit_rating_Zorka', index=False)

        # export credit_rating info data
        company_list = company_list.merge(
            company_list_simple[['org_id',
                                 'first_credit_rating_date',
                                 'last_credit_rating_date',
                                 'time_credit_rating_changes']],
            on='org_id',
            how='left'
        )
        company_list['check_duplicate'] = company_list['org_id'].duplicated(keep=False)
        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            company_list.to_excel(writer, sheet_name='company_list', index=False)


Helper.get_credit_rating()