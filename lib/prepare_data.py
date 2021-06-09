import os
from datetime import date

import pandas as pd
from pandas.api.types import CategoricalDtype
from scipy import stats

from lib.helpers import SmallFunction, DataRoot
from lib.variable_names import Variables
from statsmodels.miscmodels.ordinal_model import OrderedModel


class PrepareData(DataRoot):
    """
    Prepare data for getting descriptive statistics and running regression
    """

    def __init__(self):
        super().__init__()
        # self.cleaned_data_dict = ExtractData().extract_cleaned_data()
        self.timerange = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

    def control(self):

        # prepare data for hypothesis 1, separated by ESG rating providers and export to Excel files
        h1_refinitiv = self.hypothesis1(data=self.cleaned_data_dict['refinitiv'])
        h1_spglobal = self.hypothesis1(data=self.cleaned_data_dict['spglobal'])
        h1_sustainalytics = self.hypothesis1(data=self.cleaned_data_dict['sustainalytics'])

        # export data to Excel files
        with pd.ExcelWriter(Variables.RegressionData.H1_FILE_NAME) as writer:
            h1_refinitiv.to_excel(writer, sheet_name=Variables.RegressionData.H1_REFINITIV_SHEET_NAME, index=False)
            h1_spglobal.to_excel(writer, sheet_name=Variables.RegressionData.H1_SPGLOBAL_SHEET_NAME, index=False)
            h1_sustainalytics.to_excel(writer, sheet_name=Variables.RegressionData.H1_SUSTAINALYTICS_SHEET_NAME, index=False)

    def hypothesis1(self, data):
        """
        This function retrieves necessary data to run hypothesis 1 for corresponding ESG provider.

        The following steps are done:
            - merge ESG ratings with populated credit ratings and populated accounting data
            - NA values are excluded
            - ordinal_rating = 0 (NR) are excluded
            - create year dummies
            - create industry dummies
            - create country dummies

        :parameter data - dataframe of cleaned ESG scores of a specific ESG rating provider,
        extracted from 'cleaned_data.xlsx'.

        :return result - dataframe of regression data of a specific ESG rating provider.
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
        result = result.merge(self.cleaned_data_dict['populated_sp'],
                              on=['month', 'year', Variables.Bloomberg.BB_TICKER],
                              how='left')
        result = result.merge(self.cleaned_data_dict['control_var'],
                              on=['month', 'year', Variables.Bloomberg.BB_TICKER],
                              how='left')

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

        # merge dummies to final data on index
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
        # prepare h2
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
            Variables.ControlVar.LEV,
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
            (result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].notnull()) &
            (result[Variables.ControlVar.SIZE].notnull()) &
            (result[Variables.ControlVar.LEV].notnull()) &
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

        ####################################################################################

        h2 = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.H2_FILE_NAME), sheet_name='h2')

        h2 = pd.read_excel(os.path.join(self.cleaned_data_root, Variables.RegressionData.H2_FILE_NAME), sheet_name='h2_main')

        ####################################################################################
        # separated by firm size
        new_data = new_data.loc[new_data['AVG_SIZE'] >= new_data['AVG_SIZE'].quantile(q=0.75)]
        new_data = new_data.loc[:, (new_data != 0).any(axis=0)]  # remove redundant dummies
        ####################################################################################
        # common sample to calculate ESG ratings correlation
        common = h2.loc[
            (h2[Variables.RefinitivESG.TOTAL].notnull()) &
            (h2[Variables.SPGlobalESG.TOTAL].notnull()) &
            (h2[Variables.SustainalyticsESG.TOTAL].notnull())
            ]
        print(stats.pearsonr(common[Variables.RefinitivESG.TOTAL], common[Variables.SPGlobalESG.TOTAL]))
        print(stats.pearsonr(common[Variables.RefinitivESG.TOTAL], common[Variables.SustainalyticsESG.TOTAL]))
        print(stats.pearsonr(common[Variables.SPGlobalESG.TOTAL], common[Variables.SustainalyticsESG.TOTAL]))

        ####################################################################################

        print(stats.pearsonr(result['ESG_RATED'], result['CREDIT_RTG_CHANGE']))

        rating_type = CategoricalDtype(
            categories=sorted(result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].unique()), ordered=True)
        result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR] = result[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].astype(
            rating_type)

        # create investment grade dummies
        test.loc[test['grade'] == 'investment', 'grade_dummy'] = 1
        test.loc[test['grade'] == 'speculative', 'grade_dummy'] = 0

        ####################################################################################
        # Number of changes
        new_data = []
        for company in h2[Variables.Bloomberg.BB_TICKER].unique():
            df = h2.loc[h2[Variables.Bloomberg.BB_TICKER] == company]
            df = df.loc[df['year'] <= 2016]
            if not df.empty:
                if len(df[Variables.RegressionData.H2_ESG_RATED_DUMMY].unique()) > 1:
                    df = df.loc[df[Variables.RegressionData.H2_ESG_RATED_DUMMY] == 1]
                data_dict = {
                    Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR: df[df['CREDIT_RTG_CHANGE'] != 0].count()['CREDIT_RTG_CHANGE'],
                    'upgrade': df[df['CREDIT_RTG_CHANGE'] > 0].count()['CREDIT_RTG_CHANGE'],
                    'downgrade': df[df['CREDIT_RTG_CHANGE'] < 0].count()['CREDIT_RTG_CHANGE'],
                    'no_years': len(df['year'].unique()),
                    Variables.RegressionData.H2_ESG_RATED_DUMMY: df['ESG_RATED'].unique().item(),
                    Variables.RegressionData.H2_AVG_SIZE_VAR: df['SIZE'].mean(),
                    Variables.RegressionData.H2_AVG_LEV_VAR: df['LEVERAGE'].mean(),
                    Variables.RegressionData.H2_AVG_ICOV_VAR: df['INTEREST_COVERAGE_RATIO'].mean(),
                    Variables.RegressionData.H2_AVG_OMAR_VAR: df['OPER_MARGIN'].mean(),
                    'INDUSTRY': df['INDUSTRY'].unique().item(),
                    'COUNTRY': df['COUNTRY'].unique().item(),
                    Variables.Bloomberg.BB_TICKER: company
                }
                df_summary = pd.DataFrame.from_dict([data_dict])
                new_data.append(df_summary)
            else:
                continue
        new_data = pd.concat(new_data)
        new_data = new_data.reset_index(drop=True)

        # create LONG_TERM dummy
        new_data.loc[new_data['no_years'] > new_data['no_years'].mean(), Variables.RegressionData.H2_LONG_TERM_DUMMY] = 1
        new_data.loc[new_data['no_years'] <= new_data['no_years'].mean(), Variables.RegressionData.H2_LONG_TERM_DUMMY] = 0

        # corr
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_AVG_SIZE_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY], new_data[Variables.RegressionData.H2_AVG_SIZE_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY], new_data[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY], new_data[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY], new_data[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_ESG_RATED_DUMMY], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_SIZE_VAR], new_data[Variables.RegressionData.H2_AVG_LEV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_SIZE_VAR], new_data[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_SIZE_VAR], new_data[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_SIZE_VAR], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_LEV_VAR], new_data[Variables.RegressionData.H2_AVG_ICOV_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_LEV_VAR], new_data[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_LEV_VAR], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_ICOV_VAR], new_data[Variables.RegressionData.H2_AVG_OMAR_VAR]))
        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_ICOV_VAR], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        print(stats.pearsonr(new_data[Variables.RegressionData.H2_AVG_OMAR_VAR], new_data[Variables.RegressionData.H2_LONG_TERM_DUMMY]))

        # pair plots
        import seaborn as sns
        import matplotlib.pyplot as plt
        plt.figure(figsize=(20, 20))
        sns.pairplot(new_data,
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

        # create industry dummies
        industry_dummy = pd.get_dummies(new_data['INDUSTRY'])

        # create country dummies
        country_dummy = pd.get_dummies(new_data['COUNTRY'])

        # merge dummies to data on index
        new_data = new_data.merge(industry_dummy, how='left', left_index=True, right_index=True)
        new_data = new_data.merge(country_dummy, how='left', left_index=True, right_index=True)

        # winsorize OPER_MARGIN at 1% and 99%
        # new_data['credit_rtg_change_count'] = winsorize(new_data['credit_rtg_change_count'], limits=[0.01, 0.01])
        # new_data['AVG_SIZE'] = winsorize(new_data['AVG_SIZE'], limits=[0.05, 0.05])
        # new_data['AVG_LEV'] = winsorize(new_data['AVG_LEV'], limits=[0.05, 0.05])
        # new_data['AVG_ICOV'] = winsorize(new_data['AVG_ICOV'], limits=[0.05, 0.05])
        # new_data['AVG_OMAR'] = winsorize(new_data['AVG_OMAR'], limits=[0.05, 0.05])

        # count esg_rated
        len(new_data.loc[new_data['ESG_RATED'] == 0].index)  # 48
        len(new_data.loc[new_data['ESG_RATED'] == 1].index)  # 141

        # category type
        change_type = CategoricalDtype(categories=sorted(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].unique()), ordered=True)
        new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR] = new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].astype(change_type)

        upgrade_type = CategoricalDtype(categories=sorted(new_data['upgrade'].unique()), ordered=True)
        new_data['upgrade'] = new_data['upgrade'].astype(upgrade_type)
        downgrade_type = CategoricalDtype(categories=sorted(new_data['downgrade'].unique()), ordered=True)
        new_data['downgrade'] = new_data['downgrade'].astype(downgrade_type)


        # industry breakdown
        new_data = h2.copy(deep=True)
        new_data = new_data.loc[new_data['INDUSTRY'] == Variables.RegressionData.INDUSTRY_2]
        new_data = new_data.loc[:, (new_data != 0).any(axis=0)]  # remove redundant dummies


        full_mod_log = OrderedModel(new_data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR],
                                    new_data[[
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
        full_mod_log = OrderedModel(new_data[Variables.RegressionData.H2_CREDIT_RTG_YEARLY_CHANGE_VAR],
                                    new_data[[
                                        Variables.RegressionData.H2_ESG_RATED_DUMMY,
                                        Variables.ControlVar.SIZE,
                                        Variables.ControlVar.LEV,
                                        Variables.ControlVar.ICOV,
                                        Variables.ControlVar.OMAR,
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
        full_mod_log = OrderedModel(new_data['CREDIT_RTG_CHANGE'],
                                    new_data[[
                                        Variables.RegressionData.H2_ESG_RATED_DUMMY,
                                        Variables.ControlVar.SIZE,
                                        Variables.ControlVar.LEV,
                                        Variables.ControlVar.ICOV,
                                        Variables.ControlVar.OMAR,
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
    PrepareData().control()
    pass
