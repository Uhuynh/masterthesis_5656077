import os
import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

from lib.variable_names import Variables
from lib.helpers import ExtractData


class AnalyseData:
    """
    This class provides different methods for analyzing regression data
    """
    def __init__(self):
        self.regression_data_dict = ExtractData().extract_regression_data()

    def control(self):
        x = 1
        pass


    def descriptive_stat(self):
        """
        Returns a dataframe of descriptive statistics for regression data,
        separated by ESG rating provider.
        """
        result = pd.DataFrame()
        for key in self.regression_data_dict.keys():
            stat = self.regression_data_dict[key].describe().T
            stat['skewness'] = self.regression_data_dict[key].skew(axis=0)
            stat['kurtosis'] = self.regression_data_dict[key].kurtosis(axis=0)
            stat['hypothesis'] = key
            result = result.append(stat, ignore_index=False)
        result = result.reset_index()

        return result

    @staticmethod
    def corr_h1(data):
        """
        :parameter data: a dataframe of regression data for hypothesis 1, extracted from 'regression_data.xlsx'

        This function generates pairwise correlation coefficients and p-values.
            - scipy library is used to calculate Pearson pairwise correlation and two-sided p-values,
              for more info regarding the library:
              https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
        """
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.RegressionData.ESG_ENV_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.RegressionData.ESG_SOC_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.RegressionData.ESG_GOV_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.RegressionData.CREDIT_RTG_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_RTG_VAR], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.RegressionData.ESG_SOC_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.RegressionData.ESG_GOV_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.RegressionData.CREDIT_RTG_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_ENV_VAR], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.RegressionData.ESG_GOV_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.RegressionData.CREDIT_RTG_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_SOC_VAR], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.RegressionData.ESG_GOV_VAR], data[Variables.RegressionData.CREDIT_RTG_VAR]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_GOV_VAR], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_GOV_VAR], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_GOV_VAR], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.RegressionData.ESG_GOV_VAR], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.RegressionData.CREDIT_RTG_VAR], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data[Variables.RegressionData.CREDIT_RTG_VAR], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.RegressionData.CREDIT_RTG_VAR], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.RegressionData.CREDIT_RTG_VAR], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.SIZE], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.ControlVar.SIZE], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.ICOV], data[Variables.ControlVar.OMAR]))


    @staticmethod
    def corr_h2(data):
        """
        :parameter data: a dataframe of regression data for hypothesis 2, extracted from 'regression_data.xlsx'

        This function generates pairwise correlation coefficients and p-values.
            - scipy library is used to calculate Pearson pairwise correlation and two-sided p-values,
            for more info regarding the library:
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
        """
        print(stats.pearsonr(data['ESG_RATED'], data['CREDIT_RTG_CHANGE']))
        print(stats.pearsonr(data['ESG_RATED'], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data['ESG_RATED'], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data['ESG_RATED'], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data['ESG_RATED'], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data['CREDIT_RTG_CHANGE'], data[Variables.ControlVar.LVG]))
        print(stats.pearsonr(data['CREDIT_RTG_CHANGE'], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data['CREDIT_RTG_CHANGE'], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data['CREDIT_RTG_CHANGE'], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.SIZE]))
        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.ControlVar.LVG], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.SIZE], data[Variables.ControlVar.ICOV]))
        print(stats.pearsonr(data[Variables.ControlVar.SIZE], data[Variables.ControlVar.OMAR]))

        print(stats.pearsonr(data[Variables.ControlVar.ICOV], data[Variables.ControlVar.OMAR]))



    @staticmethod
    def pairplot(data):
        """
        :parameter data: a dataframe of regression data, extracted from 'regression_data.xlsx'

        Plotting histogram and scatter plots of regression variables
        using seaborn package.
        For more information: https://seaborn.pydata.org/generated/seaborn.pairplot.html
        """
        plt.figure(figsize=(20, 20))
        sns.pairplot(data,
                     vars=[
                         'year',
                         Variables.RegressionData.ESG_RTG_VAR,
                         Variables.RegressionData.CREDIT_RTG_VAR,
                         Variables.ControlVar.SIZE,
                         Variables.ControlVar.LVG,
                         Variables.ControlVar.ICOV,
                         Variables.ControlVar.OMAR
                     ],
                     # hue='INDUSTRY',
                     corner=True,
                     height=2,
                     aspect=1
                     )
        plt.show()

    # def check_time_range(self, cleaned_data_dict):
    #     """
    #     Return first and last available date of each company for each type of variable.
    #     """
    #     data_timerange = self.company_info[['Fundamental Ticker Equity']]
    #
    #     # extract time range of sustainalytics rating
    #     for company in cleaned_data_dict['sustainalytics']['Fundamental Ticker Equity'].unique():
    #         temp = cleaned_data_dict['sustainalytics'].loc[
    #             cleaned_data_dict['sustainalytics']['Fundamental Ticker Equity'] == company]
    #         temp = temp.sort_values(by='Dates')
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'first_sustainalytics_date'
    #         ] = list(temp['Dates'])[0]
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'last_sustainalytics_date'
    #         ] = list(temp['Dates'])[-1]
    #
    #     # extract time range of robecosam rating
    #     for company in cleaned_data_dict['robecosam']['Fundamental Ticker Equity'].unique():
    #         temp = cleaned_data_dict['robecosam'].loc[
    #             cleaned_data_dict['robecosam']['Fundamental Ticker Equity'] == company]
    #         temp = temp.sort_values(by='Dates')
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'first_robecosam_date'
    #         ] = list(temp['Dates'])[0]
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'last_robecosam_date'
    #         ] = list(temp['Dates'])[-1]
    #
    #     # extract time range of refinitiv rating
    #     for company in cleaned_data_dict['refinitiv']['Fundamental Ticker Equity'].unique():
    #         temp = cleaned_data_dict['refinitiv'].loc[
    #             cleaned_data_dict['refinitiv']['Fundamental Ticker Equity'] == company]
    #         temp = temp.sort_values(by='Dates')
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'first_refinitiv_date'
    #         ] = list(temp['Dates'])[0]
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'last_refinitiv_date'
    #         ] = list(temp['Dates'])[-1]
    #
    #     # extract first available date of credit rating
    #     for company in cleaned_data_dict['sp']['Fundamental Ticker Equity'].unique():
    #         temp = cleaned_data_dict['sp'].loc[cleaned_data_dict['sp']['Fundamental Ticker Equity'] == company]
    #         temp = temp.sort_values(by='rating_date')
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'first_credit_rtg_date'
    #         ] = list(temp['rating_date'])[0]
    #
    #     # extract time range of control variables
    #     for company in cleaned_data_dict['control_var']['Fundamental Ticker Equity'].unique():
    #         temp = cleaned_data_dict['control_var'].loc[
    #             cleaned_data_dict['control_var']['Fundamental Ticker Equity'] == company]
    #         temp = temp.sort_values(by='Dates')
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'first_accounting_date'
    #         ] = list(temp['Dates'])[0]
    #         data_timerange.loc[
    #             data_timerange['Fundamental Ticker Equity'] == company,
    #             'last_accounting_date'
    #         ] = list(temp['Dates'])[-1]
    #
    #     # convert columns from datetime to date
    #     data_timerange.iloc[:, 1:] = data_timerange.iloc[:, 1:].apply(lambda x: x.dt.date)
    #
    #     return data_timerange

    # @staticmethod
    # def count_data(cleaned_data_dict: dict):
    #     """
    #     Returns a dataframe of counted numbers of each ordinal credit rating by year
    #     """
    #     data = cleaned_data_dict['populated_sp']
    #     data = data.drop(columns=['rating_month'], index=1)
    #     data = data.loc[data['ordinal_rating'].notnull()]
    #     data = data.drop_duplicates(keep='last')
    #
    #     result = pd.DataFrame()
    #     for year in data['rating_year'].unique():
    #         data_by_year = data.loc[data['rating_year'] == year]
    #         count_dict = {}
    #         for i in range(0, 10):
    #             count_dict['rating' + str(i)] = len(data_by_year.loc[data_by_year['ordinal_rating'] == i].index)
    #         df = pd.DataFrame.from_dict(data=count_dict, orient='index').T
    #         df['total'] = len(data_by_year.index)
    #         df['year'] = year
    #         result = result.append(df, ignore_index=True)
    #     result = result.sort_values(by='year')
    #
    #     return result

    # @staticmethod
    # def corr_matrix(cleaned_data_dict: dict):
    #     """
    #     Generate correlation matrix for different ESG ratings
    #     by using data from companies that have ratings from
    #     all three providers.
    #     """
    #     # retrieve esg data
    #     robecosam = cleaned_data_dict['robecosam'][['ROBECOSAM_TOTAL_STBLY_RANK', 'Fundamental Ticker Equity', 'Dates']]
    #     refinitiv = cleaned_data_dict['refinitiv'][['TRESGS', 'Fundamental Ticker Equity', 'Dates']]
    #     sustainalytics = cleaned_data_dict['sustainalytics'][
    #         ['SUSTAINALYTICS_RANK', 'Fundamental Ticker Equity', 'Dates']]
    #
    #     # inner join
    #     df_list = [robecosam, refinitiv, sustainalytics]
    #     df_list = [df.set_index(['Fundamental Ticker Equity', 'Dates']) for df in df_list]
    #     join_df = df_list[0].join(df_list[1:])
    #
    #     corr = join_df.corr(method='pearson')  # get Pearson corr matrix
    #
    #     return corr

    # @staticmethod
    # def descriptive_statistics(cleaned_data_dict: dict, provider: str):
    #     """
    #     Return a dataframe of descriptive statistics for a rating provider year by year.
    #     *arg
    #         provider: choices are 'refinitiv' / 'robecosam' / 'sustainalytics' / 'sp'
    #     """
    #
    #     score_name = ''
    #     if provider == 'refinitiv':
    #         score_name = 'TRESGS'
    #     elif provider == 'robecosam':
    #         score_name = 'ROBECOSAM_TOTAL_STBLY_RANK'
    #     elif provider == 'sustainalytics':
    #         score_name = 'SUSTAINALYTICS_RANK'
    #     elif provider == 'sp':
    #         score_name = 'ordinal_rating'
    #
    #     data = cleaned_data_dict[provider]
    #     data['year'] = data['Dates'].dt.year
    #
    #     # get descriptive statistics by year
    #     result = pd.DataFrame()
    #     for year in data['year'].unique():
    #         data_by_year = data.loc[data['year'] == year]
    #         temp = pd.DataFrame(data_by_year[score_name].describe()).T
    #         temp['skewness'] = data_by_year[score_name].skew()
    #         temp['kurtosis'] = data_by_year[score_name].kurtosis()
    #         temp['year'] = year
    #         temp['no_companies'] = len(data_by_year['Fundamental Ticker Equity'].unique())
    #         result = result.append(temp, ignore_index=True)
    #     result = result.sort_values(by='year')
    #     result = result.round(decimals=2)
    #     return result

    # def descriptive_statistics_accounting(self, cleaned_data_dict: dict):
    #     """Returns a dataframe of descriptive statistics for accounting data"""
    #     data = cleaned_data_dict['accounting'][['SIZE',
    #                                             'LEVERAGE',
    #                                             'ROA',
    #                                             'INTEREST_COVERAGE_RATIO',
    #                                             'OPER_MARGIN',
    #                                             'company_name']]
    #
    #     # get list of companies that cannot be analyzed
    #     company_to_remove = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'),
    #                                       sheet_name='data_timerange')
    #     company_to_remove = company_to_remove.loc[
    #         (company_to_remove['first_sustainalytics_date'].isnull()) &
    #         (company_to_remove['first_robecosam_date'].isnull()) &
    #         (company_to_remove['first_refinitiv_date'].isnull())
    #         ]
    #
    #     company_to_remove = list(company_to_remove['Fundamental Ticker Equity'])
    #
    #     # exclude these companies from cleaned accounting data
    #     new_data = data[~data.company_name.isin(company_to_remove)]
    #     new_data = new_data.drop(columns=['company_name'])
    #
    #     # get descriptive statistics
    #     result = new_data.describe().T
    #     result = result.round(decimals=2)

    # def check_data_availability(self, cleaned_data_dict):
    #     """
    #     Return companies with:
    #         - at least 1 ESG rating ('esg_data' = True)
    #         - no ESG rating ('esg_data' = False).
    #         - credit rating (credit_rating = True, otherwise False)
    #     """
    #     # get list of companies
    #     company_list = pd.read_excel(os.path.join(self.cleaned_data_root, 'cleaned_data.xlsx'),
    #                                  sheet_name='company_info')
    #     company_list = company_list[['Fundamental Ticker Equity']]
    #
    #     # get sustainalytics esg rating availability
    #     sustainalytics_short = company_list.merge(
    #         cleaned_data_dict['sustainalytics'][['Fundamental Ticker Equity', 'sustainalytics_rating']],
    #         on='Fundamental Ticker Equity',
    #         how='left'
    #     )
    #     sustainalytics_short = sustainalytics_short.drop_duplicates(keep='first').reset_index(drop=True)
    #
    #     # get robecosam esg rating availability
    #     robecosam_short = company_list.merge(
    #         cleaned_data_dict['robecosam'][['Fundamental Ticker Equity', 'robecosam_rating']],
    #         on='Fundamental Ticker Equity',
    #         how='left'
    #     )
    #     robecosam_short = robecosam_short.drop_duplicates(keep='first').reset_index(drop=True)
    #
    #     # get refinitiv esg rating availability
    #     refinitiv_short = company_list.merge(
    #         cleaned_data_dict['refinitiv'][['Fundamental Ticker Equity', 'refinitiv_rating']],
    #         on='Fundamental Ticker Equity',
    #         how='left'
    #     )
    #     refinitiv_short = refinitiv_short.drop_duplicates(keep='first').reset_index(drop=True)
    #
    #     # get S&P credit rating availability
    #     sp_short = company_list.merge(
    #         cleaned_data_dict['sp'][['Fundamental Ticker Equity', 'sp_rating']],
    #         on='Fundamental Ticker Equity',
    #         how='left'
    #     )
    #     sp_short = sp_short.drop_duplicates(keep='first').reset_index(drop=True)
    #
    #     # merge all data
    #     result = sustainalytics_short.merge(robecosam_short, how='outer', on='Fundamental Ticker Equity')
    #     result = result.merge(refinitiv_short, how='outer', on='Fundamental Ticker Equity')
    #     result = result.merge(sp_short, how='outer', on='Fundamental Ticker Equity')
    #
    #     result.loc[
    #         (result['refinitiv_rating'].isnull()) &
    #         (result['robecosam_rating'].isnull()) &
    #         (result['sustainalytics_rating'].isnull()),
    #         'esg_data'
    #     ] = False
    #
    #     result.loc[
    #         (result['refinitiv_rating'].notnull()) |
    #         (result['robecosam_rating'].notnull()) |
    #         (result['sustainalytics_rating'].notnull()),
    #         'esg_data'
    #     ] = True
    #
    #     # check whether companies can be used to analyzed
    #     # 'analyze' = True if 'sp_rating' = True
    #     # 'analyze' = False if 'sp_rating' = False
    #     result.loc[result['sp_rating'].isnull(), 'analyze'] = False
    #     result.loc[result['sp_rating'].notnull(), 'analyze'] = True
    #
    #     return result




if __name__ == "__main__":
    # AnalyseData().control()
    # AnalyseData().corr(data=AnalyseData().regression_data_dict['h1_refinitiv'])
    pass
