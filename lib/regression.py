import pandas as pd
from scipy import stats
from pandas.api.types import CategoricalDtype

from lib.variable_names import Variables
from lib.helpers import ExtractData

from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.discrete.discrete_model import Logit
from scipy.stats.mstats import winsorize


class Regression:
    """
    Run regression for two hypotheses
        - statsmodels package (dev version 13.) is applied
          for more information about Ordinal Regression of statsmodels:
          https://www.statsmodels.org/devel/examples/notebooks/generated/ordinal_regression.html#Logit-ordinal-regression:
    """

    def __init__(self):
        self.regression_data_dict = ExtractData().extract_regression_data()
        pass

    def control(self):

        # run regression for hypothesis 1
        self.h1_refinitiv()
        self.h1_spglobal()
        self.h1_sustainalytics()

    def h1_refinitiv(self):
        """
        Run ordered logistic regression for hypothesis 1 with dataset from Refinitiv ESG Scores

            - Baseline model (1):
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes

            - Full model (2)
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + control variables: SIZE, LEVERAGE, INTEREST_COVERAGE_RATIO, OPER_MARGIN
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        # lagged 12 months (= 1 year)
        test = []
        for company in data[Variables.BloombergDB.BB_TICKER].unique():
            df = data.loc[data[Variables.BloombergDB.BB_TICKER] == company]
            df[Variables.RegressionData.H1_ESG_RTG_VAR] = df[Variables.RegressionData.H1_ESG_RTG_VAR].shift(periods=24)
            df[Variables.ControlVar.SIZE] = df[Variables.ControlVar.SIZE].shift(periods=12)
            df[Variables.ControlVar.LEV] = df[Variables.ControlVar.LEV].shift(periods=12)
            df[Variables.ControlVar.ICOV] = df[Variables.ControlVar.ICOV].shift(periods=12)
            df[Variables.ControlVar.OMAR] = df[Variables.ControlVar.OMAR].shift(periods=12)
            test.append(df)
        test = pd.concat(test)
        test = test.dropna(how='any')
        data = test
        data = data.loc[:, (data != 0).any(axis=0)]

        # sample breakdown
        # data = data.loc[data['year'] <= 2010]
        # data = data.loc[(data['year'] > 2010) & (data['year'] <= 2015)]
        data = data.loc[data['year'] > 2015]
        data = data.loc[:, (data != 0).any(axis=0)]  # remove redundant dummies

        # industry breakdown
        data = data.loc[data['INDUSTRY'] == 'Utility']
        data = data.loc[:, (data != 0).any(axis=0)]  # remove redundant dummies


        # quartile check for big companies
        data = data.loc[data['SIZE'] >= data['SIZE'].quantile(q=0.75)]
        data = data.loc[:, (data != 0).any(axis=0)]  # remove redundant dummies




        # convert credit rating to categorical variable
        rating_type = CategoricalDtype(categories=sorted(data[Variables.RegressionData.H1_CREDIT_RTG_VAR].unique()), ordered=True)
        data[Variables.RegressionData.H1_CREDIT_RTG_VAR] = data[Variables.RegressionData.H1_CREDIT_RTG_VAR].astype(rating_type)

        # winsorize all control variables at 5% and 95%
        # data[Variables.ControlVar.ICOV] = winsorize(data[Variables.ControlVar.ICOV], limits=[0.05, 0.05])
        # data[Variables.ControlVar.OMAR] = winsorize(data[Variables.ControlVar.OMAR], limits=[0.05, 0.05])
        # data[Variables.ControlVar.SIZE] = winsorize(data[Variables.ControlVar.SIZE], limits=[0.05, 0.05])
        # data[Variables.ControlVar.LEV] = winsorize(data[Variables.ControlVar.LEV], limits=[0.05, 0.05])

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          2007, 2008, 2009, 2010, 2011, 2012, 2013,
                                          2014, 2015, 2016, 2017, 2018, 2019,
                                          'Energy and Natural Resources', 'Utility',
                                          'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE',
                                          'GERMANY', 'GREECE', 'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG',
                                          'NETHERLANDS', 'NORWAY', 'POLAND', 'PORTUGAL', 'RUSSIA',
                                          'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LEV,
                                          Variables.ControlVar.ICOV,
                                          Variables.ControlVar.OMAR,
                                          2007, 2008, 2009, 2010, 2011, 2012, 2013,
                                          2014, 2015, 2016, 2017, 2018, 2019,
                                          'Energy and Natural Resources', 'Utility',
                                          'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE',
                                          'GERMANY', 'GREECE', 'HUNGARY', 'IRELAND', 'ITALY',
                                          'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND', 'PORTUGAL',
                                          'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                          ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

    def h1_spglobal(self):
        """
        Run ordered logistic regression for hypothesis 1 with dataset from S&P Global ESG Scores

            - Baseline model (1):
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes

            - Full model (2)
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + control variables: SIZE, LEVERAGE, INTEREST_COVERAGE_RATIO, OPER_MARGIN
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes
        """
        data = self.regression_data_dict['h1_spglobal']

        # convert credit rating to categorical variable
        rating_type = CategoricalDtype(categories=sorted(data[Variables.RegressionData.H1_CREDIT_RTG_VAR].unique()), ordered=True)
        data[Variables.RegressionData.H1_CREDIT_RTG_VAR] = data[Variables.RegressionData.H1_CREDIT_RTG_VAR].astype(
            rating_type)

        # winsorize all control variables
        data[Variables.ControlVar.ICOV] = winsorize(data[Variables.ControlVar.ICOV], limits=[0.01, 0.01])
        data[Variables.ControlVar.OMAR] = winsorize(data[Variables.ControlVar.OMAR], limits=[0.01, 0.01])
        data[Variables.ControlVar.SIZE] = winsorize(data[Variables.ControlVar.SIZE], limits=[0.01, 0.01])
        data[Variables.ControlVar.LEV] = winsorize(data[Variables.ControlVar.LEV], limits=[0.01, 0.01])

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'BELGIUM',
                                          'BRITAIN',
                                          'CZECH',
                                          'DENMARK',
                                          'FINLAND',
                                          'FRANCE',
                                          'GERMANY',
                                          'GREECE',
                                          'HUNGARY',
                                          'IRELAND',
                                          'ITALY',
                                          'LUXEMBOURG',
                                          'NETHERLANDS',
                                          'NORWAY',
                                          'PORTUGAL',
                                          'RUSSIA',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND'
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LEV,
                                          Variables.ControlVar.ICOV,
                                          Variables.ControlVar.OMAR,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'BELGIUM',
                                          'BRITAIN',
                                          'CZECH',
                                          'DENMARK',
                                          'FINLAND',
                                          'FRANCE',
                                          'GERMANY',
                                          'GREECE',
                                          'HUNGARY',
                                          'IRELAND',
                                          'ITALY',
                                          'LUXEMBOURG',
                                          'NETHERLANDS',
                                          'NORWAY',
                                          'PORTUGAL',
                                          'RUSSIA',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND'
                                          ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

    def h1_sustainalytics(self):
        """
        Run ordered logistic regression for hypothesis 1 with dataset from Sustainalytics ESG Scores

            - Baseline model (1):
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes

            - Full model (2)
                + DV: CREDIT_RTG
                + IV: ESG_RTG
                + control variables: SIZE, LEVERAGE, INTEREST_COVERAGE_RATIO, OPER_MARGIN
                + industry dummies: Yes
                + year dummies: Yes
                + country dummies: Yes
        """
        data = self.regression_data_dict['h1_sustainalytics']

        # convert credit rating to categorical variable
        rating_type = CategoricalDtype(categories=sorted(data[Variables.RegressionData.H1_CREDIT_RTG_VAR].unique()), ordered=True)
        data[Variables.RegressionData.H1_CREDIT_RTG_VAR] = data[Variables.RegressionData.H1_CREDIT_RTG_VAR].astype(
            rating_type)

        # winsorize all control variables
        data[Variables.ControlVar.ICOV] = winsorize(data[Variables.ControlVar.ICOV], limits=[0.01, 0.01])
        data[Variables.ControlVar.OMAR] = winsorize(data[Variables.ControlVar.OMAR], limits=[0.01, 0.01])
        data[Variables.ControlVar.SIZE] = winsorize(data[Variables.ControlVar.SIZE], limits=[0.01, 0.01])
        data[Variables.ControlVar.LEV] = winsorize(data[Variables.ControlVar.LEV], limits=[0.01, 0.01])

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          2015,
                                          2016,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'BELGIUM',
                                          'BRITAIN',
                                          'CZECH',
                                          'DENMARK',
                                          'FINLAND',
                                          'FRANCE',
                                          'GERMANY',
                                          'IRELAND',
                                          'ITALY',
                                          'LUXEMBOURG',
                                          'NETHERLANDS',
                                          'NORWAY',
                                          'PORTUGAL',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND',
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.H1_CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.H1_ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LEV,
                                          Variables.ControlVar.ICOV,
                                          Variables.ControlVar.OMAR,
                                          2015,
                                          2016,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'BELGIUM',
                                          'BRITAIN',
                                          'CZECH',
                                          'DENMARK',
                                          'FINLAND',
                                          'FRANCE',
                                          'GERMANY',
                                          'IRELAND',
                                          'ITALY',
                                          'LUXEMBOURG',
                                          'NETHERLANDS',
                                          'NORWAY',
                                          'PORTUGAL',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND'
                                          ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

    def h2(self):
        data = self.regression_data_dict['h2']

        # convert credit rating to categorical variable
        rating_change_type = CategoricalDtype(categories=[-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6],
                                              ordered=True)
        data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR] = data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR].astype(
            rating_change_type)

        # baseline model
        base_mod_log = OrderedModel(data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR],
                                    data[[Variables.RegressionData.H2_ESG_RATED_DUMMY,
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
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'AZERBAIJAN',
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
                                          'UKRAINE'
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.H2_CREDIT_RTG_CHANGE_VAR],
                                    data[[Variables.RegressionData.H2_ESG_RATED_DUMMY,
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
                                          'Energy and Natural Resources',
                                          'Utility',
                                          'AZERBAIJAN',
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
                                          'UKRAINE'
                                          ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        res_log.summary()


if __name__ == "__main__":
    Regression().control()
    pass
