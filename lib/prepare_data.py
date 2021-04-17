import pandas as pd
from datetime import date
import numpy as np
from pandas.api.types import CategoricalDtype

from lib.helpers import ExtractData, SmallFunction, DataRoot
from lib.variable_names import Variables


class PrepareData(DataRoot):
    """
    Prepare data for getting descriptive statistics and running regression
    """

    def __init__(self):
        super().__init__()
        self.cleaned_data_dict = ExtractData().extract_cleaned_data()
        self.timerange = SmallFunction.generate_series(start_dt=date(2006, 1, 1), end_dt=date(2020, 12, 31))

    def control(self):
        pass

    def h1_refinitiv(self):
        """
        Retrieve all data necessary to run hypothesis 1 for Refinitiv ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        refinitiv = self.cleaned_data_dict['refinitiv']
        refinitiv = refinitiv.drop(columns=['ID_ISIN', 'Dates'])

        # get industry data
        refinitiv = refinitiv.merge(self.company_info[[Variables.Bloomberg.BB_TICKER, 'INDUSTRY']],
                                    on=Variables.Bloomberg.BB_TICKER, how='left')

        # merge ESG data with time series from 2006 to 2020, group by company
        data = []
        for company in refinitiv[Variables.Bloomberg.BB_TICKER].unique():
            df = refinitiv.loc[refinitiv[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        # merge ESG data with credit ratings and accounting data
        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')

        # drop rows where there is at least 1 NA value
        data = data.dropna(how='any')

        # drop credit ratings with 'NR' values (i.e 0)
        data = data.loc[data['ordinal_rating'] != 0].reset_index(drop=True)

        # create year dummies
        year_dummy = pd.get_dummies(data['year'])

        # create industry dummies
        industry_dummy = pd.get_dummies(data['INDUSTRY'])

        # merge dummies to data on index
        data = data.merge(year_dummy, how='left', left_index=True, right_index=True)
        data = data.merge(industry_dummy, how='left', left_index=True, right_index=True)

        # convert credit rating to categorical variable
        rating_type = CategoricalDtype(categories=[1, 2, 3, 4, 5, 6, 7, 8], ordered=True)
        data['ordinal_rating'] = data['ordinal_rating'].astype(rating_type)

        # create date column
        # data['day'] = 1
        # data['time'] = pd.to_datetime(data[['year', 'month', 'day']]).dt.date
        # data = data.drop(columns=['year', 'month', 'day'])
        #
        # # run regression
        # test = data.set_index(['BB_TICKER', 'time'])
        #
        # from linearmodels import PooledOLS, PanelOLS, RandomEffects
        #
        # # Pooled OLS Regression
        # model = PanelOLS.from_formula('ordinal_rating ~ TRESGS + EntityEffects', data=test)
        # result = model.fit()
        # print(result)

        # # logit regression
        # from statsmodels.miscmodels.ordinal_model import OrderedModel
        # mod_log = OrderedModel(test['ordinal_rating'],
        #                        test[['TRESGS', 'ROA', 'LEVERAGE', 'SIZE', 'INTEREST_COVERAGE_RATIO', 'OPER_MARGIN']],
        #                        distr='logit')
        #
        # res_log = mod_log.fit(method='bfgs', disp=False)
        # res_log.summary()

        return data

    def h1_sustainalytics(self):
        """
        Retrieve all data necessary to run hypothesis 1 for Sustainalytics ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        sustainalytics = self.cleaned_data_dict['sustainalytics']
        sustainalytics = sustainalytics.drop(columns=['Dates'])

        data = []
        for company in sustainalytics[Variables.Bloomberg.BB_TICKER].unique():
            df = sustainalytics.loc[sustainalytics[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.dropna(how='any')
        data = data.loc[data['ordinal_rating'] != 0]

        # regression
        rating_type = CategoricalDtype(categories=[1, 2, 3, 4, 5, 6, 7, 8], ordered=True)
        data['ordinal_rating'] = data['ordinal_rating'].astype(rating_type)

        from statsmodels.miscmodels.ordinal_model import OrderedModel
        mod_log = OrderedModel(data['ordinal_rating'],
                               data[['SUSTAINALYTICS_RANK', 'ROA', 'LEVERAGE', 'SIZE', 'INTEREST_COVERAGE_RATIO', 'OPER_MARGIN']],
                               distr='logit')
        res_log = mod_log.fit(method='bfgs', disp=False)
        res_log.summary()

        return data

    def h1_spglobal(self):
        """
        Retrieve all data necessary to run hypothesis 1 for S&P Global ESG scores
        All NA values and where ordinal credit rating = 0 (NR) are excluded.
        """
        spglobal = self.cleaned_data_dict['robecosam']
        spglobal = spglobal.drop(columns=['Dates'])

        data = []
        for company in spglobal[Variables.Bloomberg.BB_TICKER].unique():
            df = spglobal.loc[spglobal[Variables.Bloomberg.BB_TICKER] == company]
            df = self.timerange.merge(df, on=['month', 'year'], how='left')
            data.append(df)
        data = pd.concat(data)

        data = data.merge(self.cleaned_data_dict['populated_sp'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.merge(self.cleaned_data_dict['control_var'], on=['month', 'year', Variables.Bloomberg.BB_TICKER], how='left')
        data = data.dropna(how='any')
        data = data.loc[data['ordinal_rating'] != 0]

        mod_log = OrderedModel(data['ordinal_rating'],
                               data[['ROBECOSAM_TOTAL_STBLY_RANK', 'ROA', 'LEVERAGE', 'SIZE', 'INTEREST_COVERAGE_RATIO',
                                     'OPER_MARGIN']],
                               distr='logit')
        res_log = mod_log.fit(method='bfgs', disp=False)
        res_log.summary()

        return data

    def h2_refinitiv(self):
        refinitiv = self.cleaned_data_dict['refinitiv']
        # create date column
        refinitiv['day'] = 1
        refinitiv['time'] = pd.to_datetime(refinitiv[['year', 'month', 'day']]).dt.date
        refinitiv = refinitiv.drop(columns=['year', 'month', 'day'])
        refinitiv = refinitiv.drop(columns=['ID_ISIN', 'Dates'])
        refinitiv['esg_rated'] = 1

        populated_sp = self.cleaned_data_dict['populated_sp']
        # only get credit rating during the time Refinitiv provides ESG rating
        populated_sp['day'] = 1
        populated_sp['time'] = pd.to_datetime(populated_sp[['year', 'month', 'day']]).dt.date
        populated_sp = populated_sp.drop(columns=['year', 'month', 'day'])
        populated_sp = populated_sp.loc[
            (populated_sp['time'] >= refinitiv['time'].min()) &
            (populated_sp['time'] <= refinitiv['time'].max())
            ]

        data = []
        for company in populated_sp[Variables.Bloomberg.BB_TICKER].unique():
            temp = populated_sp.loc[populated_sp[Variables.Bloomberg.BB_TICKER] == company]
            df = pd.DataFrame({
                Variables.Bloomberg.BB_TICKER: [company],
                'no_credit_rtg_changes': [(np.diff(temp['ordinal_rating']) != 0).sum()]
            })
            data.append(df)
        data = pd.concat(data)

        data = data.merge(refinitiv[[Variables.Bloomberg.BB_TICKER, 'esg_rated']].drop_duplicates(keep='first'),
                          on=Variables.Bloomberg.BB_TICKER, how='left')
        data.loc[data['esg_rated'].isnull(), 'esg_rated'] = 0

        from statsmodels.formula.api import ols
        fit = ols('no_credit_rtg_changes ~ C(esg_rated)', data=data).fit()

        fit.summary()

        return data

    def h2_sustainalytics(self):

        sustainalytics = self.cleaned_data_dict['sustainalytics']
        # create date column
        sustainalytics['day'] = 1
        sustainalytics['time'] = pd.to_datetime(sustainalytics[['year', 'month', 'day']]).dt.date
        sustainalytics = sustainalytics.drop(columns=['year', 'month', 'day'])
        sustainalytics['esg_rated'] = 1
        sustainalytics = sustainalytics.drop(columns=['Dates'])

        populated_sp = self.cleaned_data_dict['populated_sp']
        # only get credit rating during the time Refinitiv provides ESG rating
        populated_sp['day'] = 1
        populated_sp['time'] = pd.to_datetime(populated_sp[['year', 'month', 'day']]).dt.date
        populated_sp = populated_sp.drop(columns=['year', 'month', 'day'])
        populated_sp = populated_sp.loc[
            (populated_sp['time'] >= sustainalytics['time'].min()) &
            (populated_sp['time'] <= sustainalytics['time'].max())
            ]

        data = []
        for company in populated_sp[Variables.Bloomberg.BB_TICKER].unique():
            temp = populated_sp.loc[populated_sp[Variables.Bloomberg.BB_TICKER] == company]
            df = pd.DataFrame({
                Variables.Bloomberg.BB_TICKER: [company],
                'no_credit_rtg_changes': [(np.diff(temp['ordinal_rating']) != 0).sum()]
            })
            data.append(df)
        data = pd.concat(data)

        data = data.merge(sustainalytics[[Variables.Bloomberg.BB_TICKER, 'esg_rated']].drop_duplicates(keep='first'),
                          on=Variables.Bloomberg.BB_TICKER, how='left')
        data.loc[data['esg_rated'].isnull(), 'esg_rated'] = 0

        from statsmodels.formula.api import ols
        fit = ols('no_credit_rtg_changes ~ C(esg_rated)', data=data).fit()

        fit.summary()

        return data

    def h2_spglobal(self):
        spglobal = self.cleaned_data_dict['robecosam']
        spglobal = spglobal.drop(columns=['Dates'])

        # create date column
        spglobal['day'] = 1
        spglobal['time'] = pd.to_datetime(spglobal[['year', 'month', 'day']]).dt.date
        spglobal = spglobal.drop(columns=['year', 'month', 'day'])
        spglobal['esg_rated'] = 1

        populated_sp = self.cleaned_data_dict['populated_sp']
        # only get credit rating during the time Refinitiv provides ESG rating
        populated_sp['day'] = 1
        populated_sp['time'] = pd.to_datetime(populated_sp[['year', 'month', 'day']]).dt.date
        populated_sp = populated_sp.drop(columns=['year', 'month', 'day'])
        populated_sp = populated_sp.loc[
            (populated_sp['time'] >= spglobal['time'].min()) &
            (populated_sp['time'] <= spglobal['time'].max())
            ]

        data = []
        for company in populated_sp[Variables.Bloomberg.BB_TICKER].unique():
            temp = populated_sp.loc[populated_sp[Variables.Bloomberg.BB_TICKER] == company]
            df = pd.DataFrame({
                Variables.Bloomberg.BB_TICKER: [company],
                'no_credit_rtg_changes': [(np.diff(temp['ordinal_rating']) != 0).sum()]
            })
            data.append(df)
        data = pd.concat(data)

        data = data.merge(spglobal[[Variables.Bloomberg.BB_TICKER, 'esg_rated']].drop_duplicates(keep='first'),
                          on=Variables.Bloomberg.BB_TICKER, how='left')
        data.loc[data['esg_rated'].isnull(), 'esg_rated'] = 0

        from statsmodels.formula.api import ols
        fit = ols('no_credit_rtg_changes ~ C(esg_rated)', data=data).fit()

        fit.summary()

        return data






if __name__ == "__main__":
    PrepareData().control()
    pass
