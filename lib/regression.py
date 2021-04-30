import pandas as pd
from scipy import stats
from pandas.api.types import CategoricalDtype

from lib.variable_names import Variables
from lib.helpers import ExtractData

from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.discrete.discrete_model import Logit


class Regression:
    """
    Run regression for two hypotheses
        - statsmodels package is applied
          for more information about Ordinal Regression of statsmodels:
          https://www.statsmodels.org/devel/examples/notebooks/generated/ordinal_regression.html#Logit-ordinal-regression:
    """

    def __init__(self):
        self.regression_data_dict = ExtractData().extract_regression_data()

    def control(self):
        pass

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
        data = self.regression_data_dict['h1_refinitiv']

        # convert credit rating to categorical variable
        rating_type = CategoricalDtype(categories=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21], ordered=True)
        data[Variables.RegressionData.CREDIT_RTG_VAR] = data[Variables.RegressionData.CREDIT_RTG_VAR].astype(rating_type)

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
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
                                          'POLAND',
                                          'PORTUGAL',
                                          'RUSSIA',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND',
                                          'TURKEY',
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LVG,
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
                                          'POLAND',
                                          'PORTUGAL',
                                          'RUSSIA',
                                          'SPAIN',
                                          'SWEDEN',
                                          'SWITZERLAND',
                                          'TURKEY',
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
        rating_type = CategoricalDtype(categories=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], ordered=True)
        data[Variables.RegressionData.CREDIT_RTG_VAR] = data[Variables.RegressionData.CREDIT_RTG_VAR].astype(
            rating_type)

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
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
                                          'SWITZERLAND',
                                          ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        res_log.summary()
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LVG,
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
                                          'SWITZERLAND',
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
        rating_type = CategoricalDtype(categories=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], ordered=True)
        data[Variables.RegressionData.CREDIT_RTG_VAR] = data[Variables.RegressionData.CREDIT_RTG_VAR].astype(
            rating_type)

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
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
        full_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_VAR],
                                    data[[Variables.RegressionData.ESG_RTG_VAR,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LVG,
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
        data[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR] = data[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR].astype(
            rating_change_type)

        # baseline model
        base_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR],
                                    data[[Variables.RegressionData.ESG_RATED_DUMMY,
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
        full_mod_log = OrderedModel(data[Variables.RegressionData.CREDIT_RTG_CHANGE_VAR],
                                    data[[Variables.RegressionData.ESG_RATED_DUMMY,
                                          Variables.ControlVar.SIZE,
                                          Variables.ControlVar.LVG,
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

        # logit regression
        import statsmodels.api as sm

        logit_mod = sm.Logit(spector_data.endog, spector_data.exog)






if __name__ == "__main__":
    Regression().control()
    pass
