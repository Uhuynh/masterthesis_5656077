import os
from datetime import date

import pandas as pd
from pandas.api.types import CategoricalDtype
from scipy import stats
from scipy.stats.mstats import winsorize

from lib.helpers import SmallFunction, DataRoot, ExtractData
from lib.variable_names import Variables
# from statsmodels.miscmodels.ordinal_model import OrderedModel

"""
This module performs data preparation process for running regression.
More details can be found in the documentation of each function of the class below.

To execute a specific mode to see how the output is generated:
    + please scroll down to the end of the script where the clause
      if __name__ == "__main__" is placed
    + assign a string to the 'mode' variable in function PrepareData().control()
    + choices of the 'mode' variable are defined in function PrepareData().control()
"""


class PrepareData(DataRoot):
    """
    This class performs process pf preparing data for each hypothesis
    in order to get descriptive statistics and run main regression as well as robustness checks.
    """

    def __init__(self):
        super().__init__()
        self.cleaned_data_dict = ExtractData().extract_cleaned_data()
        self.bb_ticker = Variables.BloombergDB.FIELDS.BB_TICKER

    def control(self, mode='h1'):
        """
        This function prepares data for the main regression of two hypotheses and
        data for additional analyses of hypothesis 2.

        Choices of 'mode' variable are:
            - 'h1': prepare data for hypothesis 1
            - 'h2': prepare data for hypothesis 2

        Data for hypothesis 1 is then exported to Excel file under 'data/cleaned_data/h1_regression_data.xlsx'
            - dataset of Refinitiv ESG ratings is saved under sheet name 'h1_refinitiv',
            - dataset of S&P Global ESG ratings is saved under sheet name 'h1_spglobal', and
            - dataset of Sustainalytics ESG ratings is saved under sheet name 'h1_sustainalytics'.

        Data for hypothesis 2 is then exported to Excel file under 'data/cleaned_data/h2_regression_data.xlsx'
            - monthly dataset used for additional analysis is saved under sheet name 'h2_monthly',
            - yearly dataset used for additional analysis is saved under sheet name 'h2_yearly', and
            - dataset used for main regression is saved under sheet name 'h2_main'.
        """

        if mode == 'h1':

            # prepare data for hypothesis 1, separated by each ESG rating providers and export to Excel
            h1_refinitiv = self.hypothesis1(data=self.cleaned_data_dict['refinitiv'])
            h1_spglobal = self.hypothesis1(data=self.cleaned_data_dict['spglobal'])
            h1_sustainalytics = self.hypothesis1(data=self.cleaned_data_dict['sustainalytics'])

            with pd.ExcelWriter(Variables.RegressionData.FILES.H1_FILE_NAME) as writer:
                h1_refinitiv.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H1_REFINITIV_SHEET_NAME, index=False)
                h1_spglobal.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H1_SPGLOBAL_SHEET_NAME, index=False)
                h1_sustainalytics.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H1_SUSTAINALYTICS_SHEET_NAME, index=False)

        else:  # i.e mode == 'h2'

            # prepare data for main regression as well as additional analyses of hypothesis 2 and export to Excel
            h2_monthly = self.hypothesis2_monthly()
            h2_yearly = self.hypothesis2_yearly()
            h2_main = self.hypothesis2_main(h2_monthly)

            with pd.ExcelWriter(Variables.RegressionData.FILES.H2_FILE_NAME) as writer:
                h2_monthly.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H2_MONTHLY_DATA_SHEET_NAME, index=False)
                h2_yearly.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H2_YEARLY_DATA_SHEET_NAME, index=False)
                h2_main.to_excel(writer, sheet_name=Variables.RegressionData.FILES.H2_MAIN_DATA_SHEET_NAME, index=False)


    def hypothesis1(self, data) -> pd.DataFrame:
        """
        This function retrieves necessary data to run hypothesis 1 for corresponding ESG provider.

        The following steps are done:
            - merge monthly ESG ratings with monthly populated credit ratings and monthly populated accounting data
            - NA values are excluded
            - S&P credit rating = 0 (NR) are excluded
            - create year dummies
            - create industry dummies
            - create country dummies
            - winsorize all control variables at 5% and 95%

        :parameter data - dataframe of cleaned ESG scores of a specific ESG rating provider,
        extracted from 'cleaned_data.xlsx'.

        :return a dataframe of regression data of a specific ESG rating provider.
        """

        # merge ESG data with populated credit ratings and accounting data
        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', self.bb_ticker], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', self.bb_ticker], how='left')

        # drop rows where there is at least 1 NA value
        data = data.dropna(how='any')

        # drop credit ratings with 'NR' values (i.e 0)
        data = data.loc[data['ordinal_rating'] != 0].reset_index(drop=True)

        # create year dummies
        year_dummy = pd.get_dummies(data['year'])

        # get industry & country data
        data = data.merge(self.company_info[[self.bb_ticker, 'INDUSTRY', 'COUNTRY']], on=self.bb_ticker, how='left')

        # create industry dummies
        industry_dummy = pd.get_dummies(data['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(data['COUNTRY'])

        # merge dummies to final data based on index
        data = data.merge(year_dummy, how='left', left_index=True, right_index=True)
        data = data.merge(industry_dummy, how='left', left_index=True, right_index=True)
        data = data.merge(country_dummy, how='left', left_index=True, right_index=True)

        # winsorize all control variables at 5% and 95%
        data[Variables.RegressionData.ControlVar.H1_ICOV] = winsorize(data[Variables.RegressionData.ControlVar.H1_ICOV], limits=[0.05, 0.05])
        data[Variables.RegressionData.ControlVar.H1_OMAR] = winsorize(data[Variables.RegressionData.ControlVar.H1_OMAR], limits=[0.05, 0.05])
        data[Variables.RegressionData.ControlVar.H1_SIZE] = winsorize(data[Variables.RegressionData.ControlVar.H1_SIZE], limits=[0.05, 0.05])
        data[Variables.RegressionData.ControlVar.H1_LEV] = winsorize(data[Variables.RegressionData.ControlVar.H1_LEV], limits=[0.05, 0.05])

        return data

    def hypothesis2_monthly(self) -> pd.DataFrame:
        """
        Retrieve monthly data necessary to run additional analysis for hypothesis 2.

        The following steps are done:
            - calculate monthly credit rating changes
            - merge credit ratings with ESG ratings and accounting data
            - NA values are excluded
            - S&P credit rating = 0 (NR) are excluded
            - create ESG_RATED dummy (= 1 if at least 1 ESG rating available, =0 otherwise)
            - create year dummies
            - create industry dummies
            - create country dummies
        """

        # get populated credit rating
        populated_sp = self.cleaned_data_dict['populated_sp']

        # drop credit ratings with 'NR' values (i.e 0)
        populated_sp = populated_sp.loc[populated_sp['ordinal_rating'] != 0].reset_index(drop=True)

        # calculate monthly credit rating changes for each company
        result = []
        for company in populated_sp[self.bb_ticker].unique():
            df = populated_sp.loc[populated_sp[self.bb_ticker] == company]
            df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] = df['ordinal_rating'].diff(periods=1)
            df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] = df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE].shift(periods=-1)
            result.append(df)
        result = pd.concat(result)

        # merge with populated accounting data and ESG ratings from all three providers
        result = result.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', self.bb_ticker], how='left')
        result = result.merge(self.cleaned_data_dict['refinitiv'][[Variables.RefinitivESG.TOTAL,
                                                                   self.bb_ticker,
                                                                   'month',
                                                                   'year'
                                                                   ]],
                              on=['month', 'year', self.bb_ticker],
                              how='left')
        result = result.merge(self.cleaned_data_dict['spglobal'][[Variables.SPGlobalESG.TOTAL,
                                                                  self.bb_ticker,
                                                                  'month',
                                                                  'year'
                                                                  ]],
                              on=['month', 'year', self.bb_ticker],
                              how='left')
        result = result.merge(self.cleaned_data_dict['sustainalytics'][[Variables.SustainalyticsESG.TOTAL,
                                                                        self.bb_ticker,
                                                                        'month',
                                                                        'year'
                                                                        ]],
                              on=['month', 'year', self.bb_ticker],
                              how='left')

        # get industry & country data
        result = result.merge(self.company_info[[self.bb_ticker, 'INDUSTRY', 'COUNTRY']], on=self.bb_ticker, how='left')

        # remove rows where control variables have NA values
        result = result.loc[
            (result[self.bb_ticker].notnull()) &
            (result[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_SIZE].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_LEV].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_ICOV].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_OMAR].notnull()) &
            (result['INDUSTRY'].notnull()) &
            (result['COUNTRY'].notnull())
            ]

        # create dummy for ESG_RATED variable (main independent variable)
        result.loc[
            (result[Variables.SustainalyticsESG.TOTAL].notnull()) |
            (result[Variables.RefinitivESG.TOTAL].notnull()) |
            (result[Variables.SPGlobalESG.TOTAL].notnull()),
            'ESG_RATED'
        ] = 1
        result.loc[
            (result[Variables.SustainalyticsESG.TOTAL].isnull()) &
            (result[Variables.RefinitivESG.TOTAL].isnull()) &
            (result[Variables.SPGlobalESG.TOTAL].isnull()),
            'ESG_RATED'
        ] = 0

        # create year dummies
        year_dummy = pd.get_dummies(result['year'])

        # create industry dummies
        industry_dummy = pd.get_dummies(result['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(result['COUNTRY'])

        # merge dummies to data on index
        result = result.merge(year_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(country_dummy, how='left', left_index=True, right_index=True)

        return result

    def hypothesis2_yearly(self) -> pd.DataFrame:
        """
        Retrieve yearly data necessary to run additional analysis for hypothesis 2.

        The following steps are done:
            - calculate yearly credit rating changes
            - merge credit ratings with ESG ratings and accounting data
            - NA values are excluded
            - S&P credit rating = 0 (NR) are excluded
            - create ESG_RATED dummy (= 1 if at least 1 ESG rating available, =0 otherwise)
            - create year dummies
            - create industry dummies
            - create country dummies
        """
        # get populated credit rating
        populated_sp = self.cleaned_data_dict['populated_sp']

        # drop credit ratings with 'NR' values (i.e 0)
        populated_sp = populated_sp.loc[populated_sp['ordinal_rating'] != 0].reset_index(drop=True)

        # get yearly populated credit ratings
        populated_rtg_yearly = []
        for company in populated_sp[self.bb_ticker].unique():
            df = populated_sp.loc[populated_sp[self.bb_ticker] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['month'])
                df_year = df_year.loc[df_year['month'] == max_date]
                populated_rtg_yearly.append(df_year)
        populated_rtg_yearly = pd.concat(populated_rtg_yearly)
        populated_rtg_yearly = populated_rtg_yearly.drop(columns=['month'])

        # calculate yearly credit rating changes
        result = []
        for company in populated_rtg_yearly[self.bb_ticker].unique():
            df = populated_rtg_yearly.loc[populated_rtg_yearly[self.bb_ticker] == company]
            df[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE] = df['ordinal_rating'].diff(periods=1)
            df[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE] = df[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE].shift(periods=-1)
            result.append(df)
        result = pd.concat(result)

        # merge with cleaned accounting data (not populated)
        accounting = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                                   sheet_name=Variables.CleanedData.ACCOUNTING_SHEET_NAME)[[
            self.bb_ticker,
            Variables.RegressionData.ControlVar.H1_SIZE,
            Variables.RegressionData.ControlVar.H1_LEV,
            Variables.RegressionData.ControlVar.H1_ICOV,
            Variables.RegressionData.ControlVar.H1_OMAR,
            'year',
        ]]
        result = result.merge(accounting, on=[self.bb_ticker, 'year'], how='left')

        # merge with ESG ratings from all three providers
        # the cleaned data is monthly, therefore we need to convert it to yearly data
        # here we get the ESG score of the latest date of the year to be the final ESG score of that year for a company

        # merge with ESG Refinitiv ratings
        esg_refinitiv = self.cleaned_data_dict['refinitiv'][[Variables.RefinitivESG.TOTAL,
                                                             self.bb_ticker,
                                                             'month',
                                                             'year',
                                                             'Dates']]
        esg_refinitiv_yearly = []
        for company in esg_refinitiv[self.bb_ticker].unique():
            df = esg_refinitiv.loc[esg_refinitiv[self.bb_ticker] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_refinitiv_yearly.append(df_year)
        esg_refinitiv_yearly = pd.concat(esg_refinitiv_yearly)
        esg_refinitiv_yearly = esg_refinitiv_yearly.drop(columns=['month', 'Dates'])

        result = result.merge(esg_refinitiv_yearly, on=[self.bb_ticker, 'year'], how='left')

        # merge with ESG S&P Global
        esg_spglobal = self.cleaned_data_dict['spglobal'][[Variables.SPGlobalESG.TOTAL,
                                                           self.bb_ticker,
                                                           'Dates',
                                                           'year'
                                                           ]]
        esg_spglobal_yearly = []
        for company in esg_spglobal[self.bb_ticker].unique():
            df = esg_spglobal.loc[esg_spglobal[self.bb_ticker] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_spglobal_yearly.append(df_year)
        esg_spglobal_yearly = pd.concat(esg_spglobal_yearly)
        esg_spglobal_yearly = esg_spglobal_yearly.drop(columns=['Dates'])

        result = result.merge(esg_spglobal_yearly, on=[self.bb_ticker, 'year'], how='left')

        # merge with ESG Sustainalytics
        esg_sustainalytics = self.cleaned_data_dict['sustainalytics'][[Variables.SustainalyticsESG.TOTAL,
                                                                       self.bb_ticker,
                                                                       'Dates',
                                                                       'year'
                                                                       ]]
        esg_sustainalytics_yearly = []
        for company in esg_sustainalytics['BB_TICKER'].unique():
            df = esg_sustainalytics.loc[esg_sustainalytics[self.bb_ticker] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_sustainalytics_yearly.append(df_year)
        esg_sustainalytics_yearly = pd.concat(esg_sustainalytics_yearly)
        esg_sustainalytics_yearly = esg_sustainalytics_yearly.drop(columns=['Dates'])

        result = result.merge(esg_sustainalytics_yearly, on=[self.bb_ticker, 'year'], how='left')

        # get industry & country data
        result = result.merge(self.company_info[[self.bb_ticker, 'INDUSTRY', 'COUNTRY']], on=self.bb_ticker, how='left')

        # remove NAs
        result = result.loc[
            (result[self.bb_ticker].notnull()) &
            (result[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_SIZE].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_LEV].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_ICOV].notnull()) &
            (result[Variables.RegressionData.ControlVar.H1_OMAR].notnull()) &
            (result['INDUSTRY'].notnull()) &
            (result['COUNTRY'].notnull())
            ]

        # create dummy for ESG_RATED
        # dummy = 1 if has at least 1 ESG rating, = 0 otherwise
        result.loc[
            (result[Variables.SustainalyticsESG.TOTAL].notnull()) |
            (result[Variables.RefinitivESG.TOTAL].notnull()) |
            (result[Variables.SPGlobalESG.TOTAL].notnull()),
            'ESG_RATED'
        ] = 1
        result.loc[
            (result[Variables.SustainalyticsESG.TOTAL].isnull()) &
            (result[Variables.RefinitivESG.TOTAL].isnull()) &
            (result[Variables.SPGlobalESG.TOTAL].isnull()),
            'ESG_RATED'
        ] = 0

        # create year dummies
        year_dummy = pd.get_dummies(result['year'])

        # create industry dummies
        industry_dummy = pd.get_dummies(result['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(result['COUNTRY'])

        # merge dummies to data on index
        result = result.merge(year_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(country_dummy, how='left', left_index=True, right_index=True)

        return result


    def hypothesis2_main(self, h2_monthly):
        """
        Retrieve data necessary to run main regression for hypothesis 2.
        This data is generated based on data get from hypothesis2_monthly() function.

        The following steps are done:

            - calculate total number of times of credit rating changes for each company
                + for company that starts to have ESG ratings during the sample period,
                only count for credit rating changes after having ESG ratings available
                + i.e. the time when this company has no ESG rating is ignored
                    --> this helps to take into account the impact of the fact that a company switches
                    its status from non ESG-rated to ESG-rated during the sample period.

            - calculate average values of the control variables during the sample period of each company
                    --> create new control variables
                + the sample period of each company is different, depending on whether credit ratings of this company
                is available.

            - create ESG_RATED dummy
                + = 1 if at least 1 ESG rating available during the sample period of the company
                + = 0 otherwise

            - create industry dummies
            - create country dummies
        """


        # calculate total number of times of credit rating changes for each company
        # & calculate average values of the control variables during the sample period of each company
        # & create ESG_RATED dummy
        result = []
        for company in h2_monthly[self.bb_ticker].unique():
            df = h2_monthly.loc[h2_monthly[self.bb_ticker] == company]
            if not df.empty:
                if len(df[Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY].unique()) > 1:
                    df = df.loc[df[Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY] == 1]
                data_dict = {
                    Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE:
                        df[df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] != 0].count()[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE],
                    'upgrade': df[df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] > 0].count()[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE],
                    'downgrade': df[df[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] < 0].count()[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE],
                    'no_years': len(df['year'].unique()),
                    Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY: df[Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY].unique().item(),
                    Variables.RegressionData.ControlVar.H2_AVG_SIZE: df[Variables.RegressionData.ControlVar.H1_SIZE].mean(),
                    Variables.RegressionData.ControlVar.H2_AVG_LEV: df[Variables.RegressionData.ControlVar.H1_LEV].mean(),
                    Variables.RegressionData.ControlVar.H2_AVG_ICOV: df[Variables.RegressionData.ControlVar.H1_ICOV].mean(),
                    Variables.RegressionData.ControlVar.H2_AVG_OMAR: df[Variables.RegressionData.ControlVar.H1_OMAR].mean(),
                    'INDUSTRY': df['INDUSTRY'].unique().item(),
                    'COUNTRY': df['COUNTRY'].unique().item(),
                    self.bb_ticker: company
                }
                df_summary = pd.DataFrame.from_dict([data_dict])
                result.append(df_summary)
            else:
                continue
        result = pd.concat(result)
        result = result.reset_index(drop=True)

        # create LONG_TERM dummy
        # = 1 if no_years of a company > average of no_years of the whole sample (here: 9 years)
        result.loc[result['no_years'] > result['no_years'].mean(), Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY] = 1
        result.loc[result['no_years'] <= result['no_years'].mean(), Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY] = 0

        # create industry dummies
        industry_dummy = pd.get_dummies(result['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(result['COUNTRY'])

        # merge dummies to data on index
        result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(country_dummy, how='left', left_index=True, right_index=True)

        return result



        ####################################################################################

        h2_monthly = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.H2_FILE_NAME),
                                   sheet_name='h2')

        h2_monthly = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.H2_FILE_NAME),
                                   sheet_name='h2_main')

        ####################################################################################
        # separated by firm size
        result = result.loc[result['AVG_SIZE'] >= result['AVG_SIZE'].quantile(q=0.75)]
        result = result.loc[:, (result != 0).any(axis=0)]  # remove redundant dummies
        ####################################################################################
        # common sample to calculate ESG ratings correlation
        common = h2_monthly.loc[
            (h2_monthly[Variables.RefinitivESG.TOTAL].notnull()) &
            (h2_monthly[Variables.SPGlobalESG.TOTAL].notnull()) &
            (h2_monthly[Variables.SustainalyticsESG.TOTAL].notnull())
            ]
        print(stats.pearsonr(common[Variables.RefinitivESG.TOTAL], common[Variables.SPGlobalESG.TOTAL]))
        print(stats.pearsonr(common[Variables.RefinitivESG.TOTAL], common[Variables.SustainalyticsESG.TOTAL]))
        print(stats.pearsonr(common[Variables.SPGlobalESG.TOTAL], common[Variables.SustainalyticsESG.TOTAL]))

        ####################################################################################

        print(stats.pearsonr(result['ESG_RATED'], result['CREDIT_RTG_CHANGE']))

        rating_type = CategoricalDtype(
            categories=sorted(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].unique()), ordered=True)
        result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR] = result[
            Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].astype(
            rating_type)

        # create investment grade dummies
        test.loc[test['grade'] == 'investment', 'grade_dummy'] = 1
        test.loc[test['grade'] == 'speculative', 'grade_dummy'] = 0

        ####################################################################################

        # corr
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_ESG_RATED_DUMMY]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_AVG_SIZE_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(result[Variables.RegressionData.H2_ESG_RATED_DUMMY], result[Variables.RegressionData.H2_AVG_SIZE_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_ESG_RATED_DUMMY], result[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_ESG_RATED_DUMMY], result[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_ESG_RATED_DUMMY], result[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_ESG_RATED_DUMMY], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_SIZE_VAR], result[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_SIZE_VAR], result[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_SIZE_VAR], result[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_SIZE_VAR], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_LEV_VAR], result[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_LEV_VAR], result[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_LEV_VAR], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_ICOV_VAR], result[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_ICOV_VAR], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(result[Variables.RegressionData.H2_AVG_OMAR_VAR], result[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        # pair plots
        import seaborn as sns
        import matplotlib.pyplot as plt
        plt.figure(figsize=(20, 20))
        sns.pairplot(result,
                     vars=[
                         # 'year',
                         Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR,
                         Variables.RegressionData.H2_ESG_RATED_DUMMY,
                         Variables.RegressionData.H2_AVG_SIZE_VAR,
                         Variables.RegressionData.H2_AVG_LEV_VAR,
                         Variables.RegressionData.H2_AVG_ICOV_VAR,
                         Variables.RegressionData.H2_AVG_OMAR_VAR,
                         Variables.RegressionData.H2_LONG_TERM_DUMMY
                     ],
                     # hue='INDUSTRY',
                     corner=True,
                     height=2,
                     aspect=1
                     )
        plt.show()



        # winsorize OPER_MARGIN at 1% and 99%
        # new_data['credit_rtg_change_count'] = winsorize(new_data['credit_rtg_change_count'], limits=[0.01, 0.01])
        # new_data['AVG_SIZE'] = winsorize(new_data['AVG_SIZE'], limits=[0.05, 0.05])
        # new_data['AVG_LEV'] = winsorize(new_data['AVG_LEV'], limits=[0.05, 0.05])
        # new_data['AVG_ICOV'] = winsorize(new_data['AVG_ICOV'], limits=[0.05, 0.05])
        # new_data['AVG_OMAR'] = winsorize(new_data['AVG_OMAR'], limits=[0.05, 0.05])

        # count esg_rated
        len(result.loc[result['ESG_RATED'] == 0].index)  # 48
        len(result.loc[result['ESG_RATED'] == 1].index)  # 141

        # category type
        change_type = CategoricalDtype(categories=sorted(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].unique()), ordered=True)
        result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR] = result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].astype(change_type)

        upgrade_type = CategoricalDtype(categories=sorted(result['upgrade'].unique()), ordered=True)
        result['upgrade'] = result['upgrade'].astype(upgrade_type)
        downgrade_type = CategoricalDtype(categories=sorted(result['downgrade'].unique()), ordered=True)
        result['downgrade'] = result['downgrade'].astype(downgrade_type)


        # industry breakdown
        result = h2_monthly.copy(deep=True)
        result = result.loc[result['INDUSTRY'] == Variables.RegressionData.INDUSTRY_2]
        result = result.loc[:, (result != 0).any(axis=0)]  # remove redundant dummies


        full_mod_log = OrderedModel(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR],
                                    result[[
                                        Variables.RegressionData.H2_ESG_RATED_DUMMY,
                                        Variables.RegressionData.H2_AVG_SIZE_VAR,
                                        Variables.RegressionData.H2_AVG_LEV_VAR,
                                        Variables.RegressionData.H2_AVG_ICOV_VAR,
                                        Variables.RegressionData.H2_AVG_OMAR_VAR,
                                        Variables.RegressionData.H2_LONG_TERM_DUMMY,
                                        'Energy and Natural Resources', 'Utility', 'AZERBAIJAN',
                                        'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK', 'ESTONIA',
                                        'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY', 'ICELAND',
                                        'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND',
                                        'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN',
                                        'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # alternative regression model (yearly credit rating change)
        full_mod_log = OrderedModel(result[Variables.RegressionData.H2_CREDIT_RTG_YEARLY_CHANGE_VAR],
                                    result[[
                                        Variables.RegressionData.H2_ESG_RATED_DUMMY,
                                        Variables.ControlVar.H1_SIZE,
                                        Variables.ControlVar.H1_LEV,
                                        Variables.ControlVar.H1_ICOV,
                                        Variables.ControlVar.H1_OMAR,
                                        2007,
                                        2008,
                                        2009,
                                        2010,
                                        2011,
                                        2012,
                                        2013,
                                        2014,
                                        2015,
                                        2016,
                                        2017,
                                        2018,
                                        2019,
                                        'Energy and Natural Resources', 'Utility', 'AZERBAIJAN',
                                        'BELGIUM',
                                        'BRITAIN',
                                        'CROATIA',
                                        'CZECH',
                                        'DENMARK',
                                        'ESTONIA',
                                        'FINLAND',
                                        'FRANCE',
                                        'GERMANY',
                                        'GREECE',
                                        'HUNGARY',
                                        'ICELAND',
                                        'IRELAND',
                                        'ITALY',
                                        'LUXEMBOURG',
                                        'NETHERLANDS',
                                        'NORWAY',
                                        'POLAND',
                                        'PORTUGAL',
                                        'RUSSIA',
                                        'SLOVAKIA',
                                        'SLOVENIA',
                                        'SPAIN',
                                        'SWEDEN',
                                        'SWITZERLAND',
                                        'TURKEY',
                                        'UKRAINE',
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()

        # alternative regression model (monthly credit rating change)
        full_mod_log = OrderedModel(result['CREDIT_RTG_CHANGE'],
                                    result[[
                                        Variables.RegressionData.H2_ESG_RATED_DUMMY,
                                        Variables.ControlVar.H1_SIZE,
                                        Variables.ControlVar.H1_LEV,
                                        Variables.ControlVar.H1_ICOV,
                                        Variables.ControlVar.H1_OMAR,
                                        2007,
                                        2008,
                                        2009,
                                        2010,
                                        2011,
                                        2012,
                                        2013,
                                        2014,
                                        2015,
                                        2016,
                                        2017,
                                        2018,
                                        2019,
                                        2020,
                                        'Energy and Natural Resources', 'Utility', 'AZERBAIJAN',
                                        'BELGIUM',
                                        'BRITAIN',
                                        'CROATIA',
                                        'FINLAND',
                                        'FRANCE',
                                        'GERMANY',
                                        'GREECE',
                                        'HUNGARY',
                                        'ICELAND',
                                        'IRELAND',
                                        'ITALY',
                                        'LUXEMBOURG',
                                        'NETHERLANDS',
                                        'NORWAY',
                                        'PORTUGAL',
                                        'RUSSIA',
                                        'SLOVAKIA',
                                        'SPAIN',
                                        'SWEDEN',
                                        'SWITZERLAND',
                                        'TURKEY',
                                        'UKRAINE'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()

        return result






if __name__ == "__main__":
    PrepareData().control(mode='h1')

