import pandas as pd
from datetime import date
import numpy as np
from scipy.stats.mstats import winsorize

from lib.helpers import ExtractData, SmallFunction, DataRoot
from lib.variable_names import Variables


class PrepareData(DataRoot):
    """
    Prepare data for getting descriptive statistics and running regression
    """

    def __init__(self):
        super().__init__()
        # self.cleaned_data_dict = ExtractData().extract_cleaned_data()

        self.timerange = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

    def control(self):

        # prepare data for hypothesis 1, separated by ESG rating providers
        h1_refinitiv = self.hypothesis1(data=self.cleaned_data_dict['refinitiv'])
        h1_spglobal = self.hypothesis1(data=self.cleaned_data_dict['spglobal'])
        h1_sustainalytics = self.hypothesis1(data=self.cleaned_data_dict['sustainalytics'])

    def hypothesis1(self, data):
        """
        :parameter data - dataframe of cleaned ESG scores of a specific ESG rating provider

        Retrieve data necessary to run hypothesis 1 for corresponding ESG provider.

        The following steps are done:
            - merge ESG ratings with credit ratings and accounting data
            - NA values are excluded
            - ordinal_rating = 0 (NR) are excluded
            - OPER_MARGIN are winsorized at 1% and 99% level
            - create year dummies
            - create industry dummies
            - create country dummies
        """

        # get industry & country data
        data = data.merge(self.company_info[[Variables.Bloomberg.BB_TICKER, 'INDUSTRY', 'COUNTRY']],
                          on=Variables.Bloomberg.BB_TICKER, how='left')

        # merge ESG data with time series from 2006 to 2020, group by company
        result = []
        for company in data[Variables.Bloomberg.BB_TICKER].unique():
            df = data.loc[data[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            result.append(df)
        result = pd.concat(result)

        # merge ESG data with populated credit ratings and accounting data
        result = result.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        result = result.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')

        # drop rows where there is at least 1 NA value
        result = result.dropna(how='any')

        # drop credit ratings with 'NR' values (i.e 0)
        result = result.loc[result['ordinal_rating'] != 0].reset_index(drop=True)

        # create year dummies
        year_dummy = pd.get_dummies(result['year'])

        # create industry dummies
        industry_dummy = pd.get_dummies(result['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(result['COUNTRY'])

        # winsorize OPER_MARGIN at 1% and 99%
        result[Variables.ControlVar.OMAR] = winsorize(result[Variables.ControlVar.OMAR], limits=[0.01, 0.01])

        # merge dummies to data on index
        result = result.merge(year_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(country_dummy, how='left', left_index=True, right_index=True)

        return result

    # def hypothesis2(self):
    #     """
    #     Retrieve monthly data necessary to run hypothesis 2.
    #
    #     The following steps are done:
    #         - calculate monthly credit rating changes
    #         - merge credit ratings with ESG ratings and accounting data
    #         - NA values are excluded
    #         - ordinal_rating = 0 (NR) are excluded
    #         - OPER_MARGIN are winsorized at 1% and 99% level
    #         - create year dummies
    #         - create industry dummies
    #         - create country dummies
    #     """
    #
    #     # get populated credit rating
    #     populated_sp = self.cleaned_data_dict['populated_sp']
    #
    #     # drop credit ratings with 'NR' values (i.e 0)
    #     populated_sp = populated_sp.loc[populated_sp['ordinal_rating'] != 0].reset_index(drop=True)
    #
    #     # calculate credit rating changes
    #     result = []
    #     for company in populated_sp[Variables.Bloomberg.BB_TICKER].unique():
    #         df = populated_sp.loc[populated_sp[Variables.Bloomberg.BB_TICKER] == company]
    #         df['CREDIT_RTG_CHANGE'] = df['ordinal_rating'].diff(periods=1)
    #         df['CREDIT_RTG_CHANGE'] = df['CREDIT_RTG_CHANGE'].shift(periods=-1)
    #         df = self.timerange.merge(df, on=['month', 'year'], how='left')
    #         result.append(df)
    #     result = pd.concat(result)
    #
    #     # merge with accounting data and ESG ratings
    #     result = result.merge(self.cleaned_data_dict['control_var'],
    #                           on=['month', 'year', Variables.Bloomberg.BB_TICKER],
    #                           how='left')
    #     result = result.merge(self.cleaned_data_dict['refinitiv'][[Variables.RefinitivESG.TOTAL,
    #                                                                Variables.Bloomberg.BB_TICKER,
    #                                                                'month',
    #                                                                'year'
    #                                                                ]],
    #                           on=['month', 'year', Variables.Bloomberg.BB_TICKER],
    #                           how='left')
    #     result = result.merge(self.cleaned_data_dict['spglobal'][[Variables.SPGlobalESG.TOTAL,
    #                                                               Variables.Bloomberg.BB_TICKER,
    #                                                               'month',
    #                                                               'year'
    #                                                               ]],
    #                           on=['month', 'year', Variables.Bloomberg.BB_TICKER],
    #                           how='left')
    #     result = result.merge(self.cleaned_data_dict['sustainalytics'][[Variables.SustainalyticsESG.TOTAL,
    #                                                                     Variables.Bloomberg.BB_TICKER,
    #                                                                     'month',
    #                                                                     'year'
    #                                                                     ]],
    #                           on=['month', 'year', Variables.Bloomberg.BB_TICKER],
    #                           how='left')
    #
    #     # get industry & country data
    #     result = result.merge(self.company_info[[Variables.Bloomberg.BB_TICKER, 'INDUSTRY', 'COUNTRY']],
    #                           on=Variables.Bloomberg.BB_TICKER, how='left')
    #
    #
    #     # remove NAs
    #     result = result.loc[
    #         (result[Variables.Bloomberg.BB_TICKER].notnull()) &
    #         (result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR].notnull()) &
    #         (result[Variables.ControlVar.SIZE].notnull()) &
    #         (result[Variables.ControlVar.LVG].notnull()) &
    #         (result[Variables.ControlVar.ICOV].notnull()) &
    #         (result[Variables.ControlVar.OMAR].notnull()) &
    #         (result['INDUSTRY'].notnull()) &
    #         (result['COUNTRY'].notnull())
    #     ]
    #
    #     # create dummy for ESG_RATED
    #     # dummy = 1 if has at least 1 ESG rating, = 0 otherwise
    #     result.loc[
    #         (result[Variables.SustainalyticsESG.TOTAL].notnull()) |
    #         (result[Variables.RefinitivESG.TOTAL].notnull()) |
    #         (result[Variables.SPGlobalESG.TOTAL].notnull()),
    #         'ESG_RATED'
    #     ] = 1
    #     result.loc[
    #         (result[Variables.SustainalyticsESG.TOTAL].isnull()) &
    #         (result[Variables.RefinitivESG.TOTAL].isnull()) &
    #         (result[Variables.SPGlobalESG.TOTAL].isnull()),
    #         'ESG_RATED'
    #     ] = 0
    #
    #     # create year dummies
    #     year_dummy = pd.get_dummies(result['year'])
    #
    #     # create industry dummies
    #     industry_dummy = pd.get_dummies(result['INDUSTRY'])
    #
    #     # create country dummies
    #     country_dummy = pd.get_dummies(result['COUNTRY'])
    #
    #     # winsorize OPER_MARGIN at 1% and 99%
    #     result[Variables.ControlVar.OMAR] = winsorize(result[Variables.ControlVar.OMAR], limits=[0.01, 0.01])
    #
    #     # merge dummies to data on index
    #     result = result.merge(year_dummy, how='left', left_index=True, right_index=True)
    #     result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
    #     result = result.merge(country_dummy, how='left', left_index=True, right_index=True)
    #
    #     return result

    def hypothesis2(self):
        """
        Retrieve yearly data necessary to run hypothesis 2.

        The following steps are done:
            - calculate monthly credit rating changes
            - merge credit ratings with ESG ratings and accounting data
            - NA values are excluded
            - ordinal_rating = 0 (NR) are excluded
            - OPER_MARGIN are winsorized at 1% and 99% level
            - create year dummies
            - create industry dummies
            - create country dummies
        """
        import os
        # sprating = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
        #                          sheet_name=Variables.CleanedData.SP_CREDIT_RTG_SHEET_NAME)
        #
        # sprating['year'] = sprating['rating_date'].dt.year
        # sprating = sprating.sort_values(by=['BB_TICKER', 'rating_date'])
        # sprating = sprating.drop(columns=['rating_date'])
        # sprating = sprating.drop_duplicates(keep='last')
        #
        # series = pd.date_range(start=date(2006, 1, 1), end=date(2020, 12, 31), freq='1Y').to_frame()
        # series['year'] = series[0].dt.year
        # series = series[['year']].reset_index(drop=True)
        #
        # # populate (this also excludes data after 2020)
        # populated_rtg = []
        # for company in sprating[Variables.Bloomberg.BB_TICKER].unique():
        #     df = sprating.loc[sprating[Variables.Bloomberg.BB_TICKER] == company]
        #     df = series.merge(df, on=['year'], how='outer')
        #     df = df.sort_values(by=['year'])
        #     df = df.fillna(method='ffill')  # propagate last valid observation forward to next valid
        #     populated_rtg.append(df)
        # populated_rtg = pd.concat(populated_rtg)
        # populated_rtg = populated_rtg.dropna(how='any')
        # populated_rtg = populated_rtg.loc[(populated_rtg['year'] >= 2006) & (populated_rtg['year'] <= 2020)]
        # populated_rtg = populated_rtg.loc[populated_rtg['ordinal_rating'] != 0]






        populated_rtg = self.cleaned_data_dict['populated_sp']
        populated_rtg = populated_rtg.loc[populated_rtg['ordinal_rating'] != 0]
        populated_rtg_yearly = []
        for company in populated_rtg['BB_TICKER'].unique():
            df = populated_rtg.loc[populated_rtg[Variables.Bloomberg.BB_TICKER] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['month'])
                df_year = df_year.loc[df_year['month'] == max_date]
                populated_rtg_yearly.append(df_year)
        populated_rtg_yearly = pd.concat(populated_rtg_yearly)
        populated_rtg_yearly = populated_rtg_yearly.drop(columns=['month'])

        # calculate credit rating changes
        result = []
        for company in populated_rtg_yearly[Variables.Bloomberg.BB_TICKER].unique():
            df = populated_rtg_yearly.loc[populated_rtg_yearly[Variables.Bloomberg.BB_TICKER] == company]
            df['CREDIT_RTG_CHANGE'] = df['ordinal_rating'].diff(periods=1)
            df['CREDIT_RTG_CHANGE'] = df['CREDIT_RTG_CHANGE'].shift(periods=-1)
            result.append(df)
        result = pd.concat(result)

        # merge with accounting
        accounting = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.CleanedData.FILE_NAME),
                                   sheet_name=Variables.CleanedData.ACCOUNTING_SHEET_NAME)
        accounting = accounting[[
            Variables.Bloomberg.BB_TICKER,
            Variables.ControlVar.SIZE,
            Variables.ControlVar.LVG,
            Variables.ControlVar.ICOV,
            Variables.ControlVar.OMAR,
            'year',
        ]]
        result = result.merge(accounting, on=[Variables.Bloomberg.BB_TICKER, 'year'], how='left')

        # merge with ESG Refinitiv
        esg_refinitiv = self.cleaned_data_dict['refinitiv']
        esg_refinitiv = esg_refinitiv[[Variables.RefinitivESG.TOTAL,
                                       Variables.Bloomberg.BB_TICKER,
                                       'month',
                                       'year',
                                       'Dates']]
        esg_refinitiv_yearly = []
        for company in esg_refinitiv['BB_TICKER'].unique():
            df = esg_refinitiv.loc[esg_refinitiv[Variables.Bloomberg.BB_TICKER] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_refinitiv_yearly.append(df_year)
        esg_refinitiv_yearly = pd.concat(esg_refinitiv_yearly)
        esg_refinitiv_yearly = esg_refinitiv_yearly.drop(columns=['month', 'Dates'])

        result = result.merge(esg_refinitiv_yearly, on=[Variables.Bloomberg.BB_TICKER, 'year'], how='left')

        # merge with ESG S&P Global
        esg_spglobal = self.cleaned_data_dict['spglobal'][[Variables.SPGlobalESG.TOTAL,
                                                           Variables.Bloomberg.BB_TICKER,
                                                           'Dates',
                                                           'year'
                                                           ]]
        esg_spglobal_yearly = []
        for company in esg_spglobal['BB_TICKER'].unique():
            df = esg_spglobal.loc[esg_spglobal[Variables.Bloomberg.BB_TICKER] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_spglobal_yearly.append(df_year)
        esg_spglobal_yearly = pd.concat(esg_spglobal_yearly)
        esg_spglobal_yearly = esg_spglobal_yearly.drop(columns=['Dates'])

        result = result.merge(esg_spglobal_yearly, on=[Variables.Bloomberg.BB_TICKER, 'year'], how='left')

        # merge with ESG Sustainalytics
        esg_sustainalytics = self.cleaned_data_dict['sustainalytics'][[Variables.SustainalyticsESG.TOTAL,
                                                                       Variables.Bloomberg.BB_TICKER,
                                                                       'Dates',
                                                                       'year'
                                                                       ]]
        esg_sustainalytics_yearly = []
        for company in esg_sustainalytics['BB_TICKER'].unique():
            df = esg_sustainalytics.loc[esg_sustainalytics[Variables.Bloomberg.BB_TICKER] == company]
            for year in df['year'].unique():
                df_year = df.loc[df['year'] == year]
                max_date = max(df_year['Dates'])
                df_year = df_year.loc[df_year['Dates'] == max_date]
                esg_sustainalytics_yearly.append(df_year)
        esg_sustainalytics_yearly = pd.concat(esg_sustainalytics_yearly)
        esg_sustainalytics_yearly = esg_sustainalytics_yearly.drop(columns=['Dates'])

        result = result.merge(esg_sustainalytics_yearly, on=[Variables.Bloomberg.BB_TICKER, 'year'], how='left')

        # get industry & country data
        result = result.merge(self.company_info[[Variables.Bloomberg.BB_TICKER, 'INDUSTRY', 'COUNTRY']],
                              on=Variables.Bloomberg.BB_TICKER, how='left')

        # remove NAs
        result = result.loc[
            (result[Variables.Bloomberg.BB_TICKER].notnull()) &
            (result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR].notnull()) &
            (result[Variables.ControlVar.SIZE].notnull()) &
            (result[Variables.ControlVar.LVG].notnull()) &
            (result[Variables.ControlVar.ICOV].notnull()) &
            (result[Variables.ControlVar.OMAR].notnull()) &
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








        h2 = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.FILE_NAME),
                           sheet_name='h2_yearly')



        # from pandas.api.types import CategoricalDtype
        # from statsmodels.miscmodels.ordinal_model import OrderedModel
        # sorted(result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR].unique())
        # from scipy import stats
        # print(stats.pearsonr(result['ESG_RATED'], result['CREDIT_RTG_CHANGE']))
        #
        # rating_type = CategoricalDtype(
        #     categories=[-7.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], ordered=True)
        # result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR] = result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR].astype(
        #     rating_type)
        #
        # base_mod_log = OrderedModel(result[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR],
        #                             result[[Variables.RegressionData.ESG_RATED_DUMMY
        #                                     ]],
        #                             distr='logit')
        # res_log = base_mod_log.fit(method='bfgs')
        # res_log.summary()

        import statsmodels.api as sm
        log_reg = sm.Logit(h2[['grade_dummy']],
                           h2[[Variables.RegressionData.ESG_RATED_DUMMY]]).fit()
        print(log_reg.summary())



        formula1 = 'CREDIT_RTG_CHANGE ~ ESG_RATED'
        model1 = sm.Logit(formula1, h2)
        result1 = model1.fit(cov_type='HC1')
        print(result1.summary())




        # create investment grade dummies
        h2.loc[h2['grade'] == 'investment', 'grade_dummy'] = 1
        h2.loc[h2['grade'] == 'speculative', 'grade_dummy'] = 0




        # create year dummies
        year_dummy = pd.get_dummies(result['year'])

        # create industry dummies
        industry_dummy = pd.get_dummies(result['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(result['COUNTRY'])

        # winsorize OPER_MARGIN at 1% and 99%
        result[Variables.ControlVar.OMAR] = winsorize(result[Variables.ControlVar.OMAR], limits=[0.01, 0.01])

        # merge dummies to data on index
        result = result.merge(year_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(industry_dummy, how='left', left_index=True, right_index=True)
        result = result.merge(country_dummy, how='left', left_index=True, right_index=True)

        return result


if __name__ == "__main__":
    PrepareData().control()
    pass
