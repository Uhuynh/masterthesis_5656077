import pandas as pd
from pandas.api.types import CategoricalDtype

from lib.variable_names import Variables
from lib.helpers import ExtractData
from lib.prepare_data import PrepareData

from statsmodels.miscmodels.ordinal_model import OrderedModel

"""
This module runs regression for both hypotheses in the thesis.
More details can be found in the documentation of each function of the class below.

To execute a specific mode to see how the output is generated:
    + please scroll down to the end of the script where the clause
      if __name__ == "__main__" is placed
    + assign a string to the 'mode' variable in function Regression().control()
    + choices of the 'mode' variable are defined in function Regression().control()

statsmodels package (dev version 13.) is applied.
For more information about Ordinal Regression of statsmodels:
https://www.statsmodels.org/devel/examples/notebooks/generated/ordinal_regression.html#Logit-ordinal-regression

It is important to successfully install the required version before running this module
https://www.statsmodels.org/devel/install.html
or one can simply run 'git clone git://github.com/statsmodels/statsmodels.git' in the console and mark the statsmodels as
source directory.
"""


class Regression:
    """
    Run main regression as well as additional analyses for two hypotheses
    """

    def __init__(self):
        self.regression_data_dict = ExtractData().extract_regression_data()

    def control(self, mode='main'):
        """
        This function runs main regressions and additional analyses for both hypotheses.

        Choices of 'mode' variable are:
            - 'main': run main regression for both hypotheses (note: this may take long time)
            - 'sub-periods': run additional analyses for sub sample periods for both hypotheses (note: this may take long time)
            - 'industry-breakdown': run additional analyses for a single industry for both hypotheses (note: this may take long time)
            - 'endogeneity': run endogeneity check for hypothesis 1
            - 'alternative-model': run alternative regression models for hypothesis 2
            - 'size-impact': run additional analyses for size impact for hypothesis 1

        The results will be printed out in the console.
        Note: the regression may take long time to execute and print results in the console.
        """

        if mode == 'main':
            self.h1_refinitiv()
            self.h1_spglobal()
            self.h1_sustainalytics()
            self.h2_main()

        # additional analysis

        elif mode == 'sub-periods':
            self.h1_refinitiv_sub_sample_periods()
            self.h2_main_sub_sample_periods()

        elif mode == 'industry-breakdown':
            self.h1_refinitiv_industry_breakdown()
            self.h2_main_industry_breakdown()

        elif mode == 'endogeneity':
            self.h1_refinitiv_lagged()

        elif mode == 'alternative-model':
            self.h2_alternative_models()

        elif mode == 'size-impact':
            self.h1_size_impact()

    def h1_refinitiv(self) -> None:
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

        The regression results are printed in the console and are used to report table 6 in the thesis.
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = data[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        2007, 2008, 2009, 2010, 2011, 2012, 2013,
                                        # year dummies (exclude one year, which is used as reference)
                                        2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        # industry dummies (exclude one industry, which is used as reference)
                                        'BELGIUM',  # country dummies (exclude one country, which is used as reference)
                                        'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE',
                                        'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY',
                                        'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                    ]],
                                    distr='logit')
        res_log = base_mod_log.fit(method='bfgs')
        print('Main result for baseline regression of hypothesis 1 using dataset from Refinitiv...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                          Variables.RegressionData.ControlVar.H1_SIZE,
                                          Variables.RegressionData.ControlVar.H1_LEV,
                                          Variables.RegressionData.ControlVar.H1_ICOV,
                                          Variables.RegressionData.ControlVar.H1_OMAR,
                                          2007, 2008, 2009, 2010, 2011, 2012,
                                          2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                          'Energy and Natural Resources', 'Utility',
                                          'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY',
                                          'GREECE', 'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS',
                                          'NORWAY',
                                          'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                          ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h1_spglobal(self) -> None:
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

        The regression results are printed in the console and are used to report table 6 in the thesis.
        """
        data = self.regression_data_dict['h1_spglobal']

        # convert credit rating to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = data[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                          2017,  # year dummies (exclude one year, which is used as reference)
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          # industry dummies (exclude one industry, which is used as reference)
                                          'Utility',
                                          'BELGIUM',
                                          # country dummies (exclude one country, which is used as reference)
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
        print('Main result for baseline regression of hypothesis 1 using dataset from S&P Global...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                          Variables.RegressionData.ControlVar.H1_SIZE,
                                          Variables.RegressionData.ControlVar.H1_LEV,
                                          Variables.RegressionData.ControlVar.H1_ICOV,
                                          Variables.RegressionData.ControlVar.H1_OMAR,
                                          2017,  # year dummies (exclude one year, which is used as reference)
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          # industry dummies (exclude one industry, which is used as reference)
                                          'Utility',
                                          'BELGIUM',
                                          # country dummies (exclude one country, which is used as reference)
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
        print('Main result for full regression of hypothesis 1 using dataset from S&P Global...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
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

        The regression results are printed in the console and are used to report table 6 in the thesis.
        """
        data = self.regression_data_dict['h1_sustainalytics']

        # convert credit rating to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = data[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logit regression

        # baseline model (1)
        base_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                          2015,  # year dummies (exclude one year, which is used as reference)
                                          2016,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          # industry dummies (exclude one industry, which is used as reference)
                                          'Utility',
                                          'BELGIUM',
                                          # country dummies (exclude one country, which is used as reference)
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
        print('Main result for baseline regression of hypothesis 1 using dataset from Sustainalytics...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        # full model (2)
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    data[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                          Variables.RegressionData.ControlVar.H1_SIZE,
                                          Variables.RegressionData.ControlVar.H1_LEV,
                                          Variables.RegressionData.ControlVar.H1_ICOV,
                                          Variables.RegressionData.ControlVar.H1_OMAR,
                                          2015,  # year dummies (exclude one year, which is used as reference)
                                          2016,
                                          2017,
                                          2018,
                                          2019,
                                          2020,
                                          'Energy and Natural Resources',
                                          # industry dummies (exclude one industry, which is used as reference)
                                          'Utility',
                                          'BELGIUM',
                                          # country dummies (exclude one country, which is used as reference)
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
        print('Main result for full regression of hypothesis 1 using dataset from Sustainalytics...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h2_main(self) -> None:
        """
        Run ordered logistic (main) regression for hypothesis 2

            - Baseline model (1):
                + DV: CR_CHANGE
                + IV: ESG_RATED
                + industry dummies: Yes
                + country dummies: Yes

            - Extended model (2)
                + DV: CR_CHANGE
                + IV: ESG_RATED
                + control variables: SIZE, LEVERAGE, INTEREST_COVERAGE_RATIO, OPER_MARGIN
                + industry dummies: Yes
                + country dummies: Yes

            - Full model (3)
                + DV: CR_CHANGE
                + IV: ESG_RATED
                + control variables: SIZE, LEVERAGE, INTEREST_COVERAGE_RATIO, OPER_MARGIN, LONG_TERM
                + industry dummies: Yes
                + country dummies: Yes

        The regression results are printed in the console and are used to report table 6 in the thesis.

        """
        data = self.regression_data_dict['h2_main'].copy(deep=True)

        # convert credit rating changes to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()), ordered=True)
        data[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = data[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # baseline model (1)
        extended_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                        data[[
                                            Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                            'Energy and Natural Resources', 'Utility',
                                            'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK',
                                            'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY',
                                            'ICELAND', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY',
                                            'POLAND', 'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SLOVENIA',
                                            'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                        ]],
                                        distr='logit')
        res_log = extended_mod_log.fit(method='bfgs')
        print('Main result for baseline regression of hypothesis 2 ...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        # extended model (2)
        extended_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                        data[[
                                            Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                            Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                            Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                            Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                            Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                            'Energy and Natural Resources', 'Utility',
                                            'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK',
                                            'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY',
                                            'ICELAND', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS',
                                            'NORWAY', 'POLAND', 'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SLOVENIA',
                                            'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                        ]],
                                        distr='logit')
        res_log = extended_mod_log.fit(method='bfgs')
        print('Main result for extended regression of hypothesis 2 ...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        # full model (3)
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                    data[[
                                        Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                        Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                        Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                        Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                        Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                        Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                        'Energy and Natural Resources', 'Utility',
                                        'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK', 'ESTONIA',
                                        'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY', 'ICELAND', 'IRELAND',
                                        'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND', 'PORTUGAL', 'RUSSIA',
                                        'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 2 ...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h1_refinitiv_sub_sample_periods(self) -> None:
        """
        Re-run full regression as in h1_refinitiv() but breaking the sample into smaller periods:
            - 2006 -> 2012
            - 2013 -> 2019
            - 2006 -> 2010
            - 2011 -> 2015
            - 2016 -> 2019

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix B of the thesis.
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        #
        # 2006 - 2012
        #
        sub_data1 = data.loc[(data['year'] >= 2006) & (data['year'] <= 2012)].copy(deep=True)
        sub_data1 = sub_data1.loc[:, (sub_data1 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data1[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data1[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2007, 2008, 2009, 2010, 2011, 2012,
                                        'Energy and Natural Resources', 'Utility',
                                        'BELGIUM', 'BRITAIN', 'CZECH', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE',
                                        'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY',
                                        'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv between 2006 and 2012...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # 2013 - 2019
        #
        sub_data2 = data.loc[(data['year'] >= 2013) & (data['year'] <= 2019)].copy(deep=True)
        sub_data2 = sub_data2.loc[:, (sub_data2 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data2[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data2[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                               Variables.RegressionData.ControlVar.H1_SIZE,
                                               Variables.RegressionData.ControlVar.H1_LEV,
                                               Variables.RegressionData.ControlVar.H1_ICOV,
                                               Variables.RegressionData.ControlVar.H1_OMAR,
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
                                               'TURKEY'
                                               ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv between 2013 and 2019...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # 2006 - 2010
        #
        sub_data3 = data.loc[(data['year'] >= 2006) & (data['year'] <= 2010)].copy(deep=True)
        sub_data3 = sub_data3.loc[:, (sub_data3 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data3[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data3[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                               Variables.RegressionData.ControlVar.H1_SIZE,
                                               Variables.RegressionData.ControlVar.H1_LEV,
                                               Variables.RegressionData.ControlVar.H1_ICOV,
                                               Variables.RegressionData.ControlVar.H1_OMAR,
                                               2007,
                                               2008,
                                               2009,
                                               2010,
                                               'Energy and Natural Resources',
                                               'Utility',
                                               'BELGIUM',
                                               'BRITAIN',
                                               'CZECH',
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
                                               'TURKEY'
                                               ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv between 2006 and 2010...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # 2011 - 2015
        #
        sub_data4 = data.loc[(data['year'] >= 2011) & (data['year'] <= 2015)].copy(deep=True)
        sub_data4 = sub_data4.loc[:, (sub_data4 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data4[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data4[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data4[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data4[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data4[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                               Variables.RegressionData.ControlVar.H1_SIZE,
                                               Variables.RegressionData.ControlVar.H1_LEV,
                                               Variables.RegressionData.ControlVar.H1_ICOV,
                                               Variables.RegressionData.ControlVar.H1_OMAR,
                                               2012,
                                               2013,
                                               2014,
                                               2015,
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
                                               'TURKEY'
                                               ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv between 2011 and 2015...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # 2016 - 2019
        #
        sub_data5 = data.loc[(data['year'] >= 2016) & (data['year'] <= 2019)].copy(deep=True)
        sub_data5 = sub_data5.loc[:, (sub_data5 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data5[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data5[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data5[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data5[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data5[[Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                               Variables.RegressionData.ControlVar.H1_SIZE,
                                               Variables.RegressionData.ControlVar.H1_LEV,
                                               Variables.RegressionData.ControlVar.H1_ICOV,
                                               Variables.RegressionData.ControlVar.H1_OMAR,
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
                                               'PORTUGAL',
                                               'RUSSIA',
                                               'SPAIN',
                                               'SWEDEN',
                                               'SWITZERLAND',
                                               'TURKEY'
                                               ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using dataset from Refinitiv between 2016 and 2019...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h2_main_sub_sample_periods(self) -> None:
        """
        Re-run full regression as in h2_main() but breaking the sample into smaller periods:
            - 2006 -> 2016
            - 2010 -> 2019

        Reason for code repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix B of the thesis.
        """

        #
        # 2006 - 2016
        #

        # re-generate data
        sub_data1 = PrepareData().hypothesis2_main(h2_monthly=self.regression_data_dict['h2_monthly'], start_year=2006,
                                                   end_year=2016)

        # convert credit rating changes to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = sub_data1[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log1 = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                     sub_data1[[Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                                Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                                Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                                Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                                Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                                Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                                'Energy and Natural Resources', 'Utility',
                                                'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK',
                                                'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY',
                                                'ICELAND',
                                                'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND',
                                                'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN',
                                                'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                                ]],
                                     distr='logit')
        res_log1 = full_mod_log1.fit(method='bfgs')
        print('Main result for full regression of hypothesis 2 between 2006 and 2016 ...')
        print(res_log1.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log1.prsquared)

        #
        # 2010 - 2019
        #

        # re-generate data
        sub_data2 = PrepareData().hypothesis2_main(h2_monthly=self.regression_data_dict['h2_monthly'], start_year=2010,
                                                   end_year=2019)

        # convert credit rating changes to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = sub_data2[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log2 = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                     sub_data2[[Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                                Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                                Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                                Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                                Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                                Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                                'Energy and Natural Resources', 'Utility',
                                                'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK',
                                                'ESTONIA', 'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY',
                                                'ICELAND',
                                                'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND',
                                                'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN',
                                                'SWITZERLAND', 'TURKEY', 'UKRAINE'
                                                ]],
                                     distr='logit')
        res_log2 = full_mod_log2.fit(method='bfgs')
        print('Main result for full regression of hypothesis 2 between 2010 and 2019 ...')
        print(res_log2.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log2.prsquared)

    def h1_refinitiv_industry_breakdown(self) -> None:
        """
        Re-run full regression as in h1_refinitiv() but breaking the sample into a single industry:
            - 'Aerospace/Automotive/Capital Goods/Metal'
            - 'Energy and Natural Resources'
            - 'Utility'

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix C of the thesis.
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        #
        # Aerospace/Automotive/Capital Goods/Metal
        #
        sub_data1 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_1].copy(deep=True)
        sub_data1 = sub_data1.loc[:, (sub_data1 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data1[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log1 = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                     sub_data1[[
                                         Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                         Variables.RegressionData.ControlVar.H1_SIZE,
                                         Variables.RegressionData.ControlVar.H1_LEV,
                                         Variables.RegressionData.ControlVar.H1_ICOV,
                                         Variables.RegressionData.ControlVar.H1_OMAR,
                                         2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                         'BRITAIN', 'FINLAND', 'FRANCE', 'GERMANY', 'IRELAND', 'ITALY',
                                         'LUXEMBOURG', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY'
                                     ]],
                                     distr='logit')
        res_log1 = full_mod_log1.fit(method='bfgs')
        print(
            'Main result of full regression of hypothesis 1 using Refinitiv dataset, separated by Aerospace/Automotive/Capital Goods/Metal industry...')
        print(res_log1.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log1.prsquared)

        #
        # Energy and Natural Resources
        #
        sub_data2 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_2].copy(deep=True)
        sub_data2 = sub_data2.loc[:, (sub_data2 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data2[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log2 = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                     sub_data2[[
                                         Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                         Variables.RegressionData.ControlVar.H1_SIZE,
                                         Variables.RegressionData.ControlVar.H1_LEV,
                                         Variables.RegressionData.ControlVar.H1_ICOV,
                                         Variables.RegressionData.ControlVar.H1_OMAR,
                                         2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                         'BRITAIN', 'DENMARK', 'FRANCE', 'HUNGARY', 'ITALY', 'NETHERLANDS',
                                         'NORWAY', 'RUSSIA', 'SPAIN'
                                     ]],
                                     distr='logit')
        res_log2 = full_mod_log2.fit(method='bfgs')
        print(
            'Main result of full regression of hypothesis 1 using Refinitiv dataset, separated by Energy and Natural Resources industry...')
        print(res_log2.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log2.prsquared)

        #
        # Utility
        #
        sub_data3 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_3].copy(deep=True)
        sub_data3 = sub_data3.loc[:, (sub_data3 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data3[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log3 = OrderedModel(sub_data3[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                     sub_data3[[
                                         Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                         Variables.RegressionData.ControlVar.H1_SIZE,
                                         Variables.RegressionData.ControlVar.H1_LEV,
                                         Variables.RegressionData.ControlVar.H1_ICOV,
                                         Variables.RegressionData.ControlVar.H1_OMAR,
                                         2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                         'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY',
                                         'GREECE', 'ITALY', 'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN'
                                     ]],
                                     distr='logit')
        res_log3 = full_mod_log3.fit(method='bfgs')
        print(
            'Main result of full regression of hypothesis 1 using Refinitiv dataset, separated by Utility industry...')
        print(res_log3.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log3.prsquared)

    def h2_main_industry_breakdown(self) -> None:
        """
        Re-run full regression as in h2_main() but breaking the sample into a single industry:
            - 'Aerospace/Automotive/Capital Goods/Metal'
            - 'Energy and Natural Resources'
            - 'Utility'

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix C of the thesis.
        """
        data = self.regression_data_dict['h2_main'].copy(deep=True)

        #
        # Aerospace/Automotive/Capital Goods/Metal
        #
        sub_data1 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_1].copy(deep=True)
        sub_data1 = sub_data1.loc[:, (sub_data1 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = sub_data1[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log1 = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                     sub_data1[[
                                         Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                         Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                         Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                         Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                         Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                         Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                         'BRITAIN', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY',
                                         'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'RUSSIA', 'SPAIN',
                                         'SWEDEN', 'SWITZERLAND', 'TURKEY'
                                     ]],
                                     distr='logit')
        res_log1 = full_mod_log1.fit(method='bfgs')
        print(
            'Main result of full regression of hypothesis 2, separated by Aerospace/Automotive/Capital Goods/Metal industry...')
        print(res_log1.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log1.prsquared)

        #
        # Energy and Natural Resources
        #
        sub_data2 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_2].copy(deep=True)
        sub_data2 = sub_data2.loc[:, (sub_data2 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = sub_data2[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log2 = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                     sub_data2[[
                                         Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                         Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                         Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                         Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                         Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                         Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                         'BELGIUM', 'BRITAIN', 'DENMARK', 'FRANCE', 'HUNGARY', 'ITALY',
                                         'NETHERLANDS', 'NORWAY', 'RUSSIA', 'SLOVENIA', 'SPAIN', 'UKRAINE'
                                     ]],
                                     distr='logit')
        res_log2 = full_mod_log2.fit(method='bfgs')
        print('Main result of full regression of hypothesis 2, separated by Energy and Natural Resources industry...')
        print(res_log2.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log2.prsquared)

        #
        # Utility
        #
        sub_data3 = data.loc[data['INDUSTRY'] == Variables.RegressionData.INDUSTRY.INDUSTRY_3].copy(deep=True)
        sub_data3 = sub_data3.loc[:, (sub_data3 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data3[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        sub_data3[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE] = sub_data3[
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log3 = OrderedModel(sub_data3[Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE],
                                     sub_data3[[
                                         Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                         Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                                         Variables.RegressionData.ControlVar.H2_AVG_LEV,
                                         Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                                         Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                                         Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
                                         'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK', 'ESTONIA', 'FINLAND',
                                         'FRANCE',
                                         'GERMANY', 'GREECE', 'ICELAND', 'IRELAND', 'ITALY', 'NETHERLANDS',
                                         'NORWAY', 'POLAND', 'PORTUGAL', 'RUSSIA', 'SLOVAKIA', 'SPAIN', 'SWEDEN'
                                     ]],
                                     distr='logit')
        res_log3 = full_mod_log3.fit(method='lbfgs')
        print('Main result of full regression of hypothesis 2, separated by Utility industry...')
        print(res_log3.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log3.prsquared)

    def h1_refinitiv_lagged(self) -> None:
        """
        Re-run full regression as in h1_refinitiv() but lagging the independent variables:
            - ESG_RTG lagged by 12 months or 24 months
            - financial control variables lagged by 12 months

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix D of the thesis.
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        #
        # lagged 12 months
        #
        sub_data1 = []
        for company in data[Variables.BloombergDB.FIELDS.BB_TICKER].unique():
            df = data.loc[data[Variables.BloombergDB.FIELDS.BB_TICKER] == company]
            df[Variables.RegressionData.IndependentVar.H1_ESG_RTG] = df[
                Variables.RegressionData.IndependentVar.H1_ESG_RTG].shift(periods=12)
            df[Variables.RegressionData.ControlVar.H1_SIZE] = df[Variables.RegressionData.ControlVar.H1_SIZE].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_LEV] = df[Variables.RegressionData.ControlVar.H1_LEV].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_ICOV] = df[Variables.RegressionData.ControlVar.H1_ICOV].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_OMAR] = df[Variables.RegressionData.ControlVar.H1_OMAR].shift(
                periods=12)
            sub_data1.append(df)
        sub_data1 = pd.concat(sub_data1)
        sub_data1 = sub_data1.dropna(how='any')
        sub_data1 = sub_data1.loc[:, (sub_data1 != 0).any(axis=0)]

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data1[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        full_mod_log = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data1[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY',
                                        'GREECE', 'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY',
                                        'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print(
            'Main result for full regression of hypothesis 1 using dataset from Refinitiv with explanatory variables lagged by 12 months...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # ESG_RTG lagged 24 months, control variables lagged 12 months
        #
        sub_data2 = []
        for company in data[Variables.BloombergDB.FIELDS.BB_TICKER].unique():
            df = data.loc[data[Variables.BloombergDB.FIELDS.BB_TICKER] == company]
            df[Variables.RegressionData.IndependentVar.H1_ESG_RTG] = df[
                Variables.RegressionData.IndependentVar.H1_ESG_RTG].shift(periods=24)
            df[Variables.RegressionData.ControlVar.H1_SIZE] = df[Variables.RegressionData.ControlVar.H1_SIZE].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_LEV] = df[Variables.RegressionData.ControlVar.H1_LEV].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_ICOV] = df[Variables.RegressionData.ControlVar.H1_ICOV].shift(
                periods=12)
            df[Variables.RegressionData.ControlVar.H1_OMAR] = df[Variables.RegressionData.ControlVar.H1_OMAR].shift(
                periods=12)
            sub_data2.append(df)
        sub_data2 = pd.concat(sub_data2)
        sub_data2 = sub_data2.dropna(how='any')
        sub_data2 = sub_data2.loc[:, (sub_data2 != 0).any(axis=0)]

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data2[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        full_mod_log = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data2[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        'BELGIUM', 'BRITAIN', 'CZECH', 'DENMARK', 'FINLAND', 'FRANCE', 'GERMANY',
                                        'GREECE', 'HUNGARY', 'IRELAND', 'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY',
                                        'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print(
            'Main result for full regression of hypothesis 1 using dataset from Refinitiv with explanatory variables lagged by 24 months...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h2_alternative_models(self):
        """
        Run regression for hypothesis 2 but using monthly and yearly credit rating changes as dependent variables.

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix E of the thesis.
        """

        #
        # monthly credit rating changes as dependent variable
        #
        data = self.regression_data_dict['h2_monthly'].copy(deep=True)

        # convert credit rating changes to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        data[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE] = data[
            Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H2_MONTHLY_CREDIT_RTG_CHANGE],
                                    data[[
                                        Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2007, 2008, 2009, 2010, 2011, 2012, 2013,
                                        2014, 2015, 2016, 2017, 2018, 2019, 2020,
                                        'Energy and Natural Resources', 'Utility',
                                        'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK', 'ESTONIA',
                                        'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY', 'ICELAND', 'IRELAND',
                                        'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND', 'PORTUGAL',
                                        'RUSSIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                        'UKRAINE'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print(
            'Main result for full regression of hypothesis 2 with monthly credit rating changes as dependent variable ...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # yearly credit rating changes as dependent variable
        #
        data = self.regression_data_dict['h2_yearly'].copy(deep=True)

        # convert credit rating changes to categorical variable
        change_type = CategoricalDtype(
            categories=sorted(data[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE].unique()),
            ordered=True)
        data[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE] = data[
            Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(data[Variables.RegressionData.DependentVar.H2_YEARLY_CREDIT_RTG_CHANGE],
                                    data[[
                                        Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2007, 2008, 2009, 2010, 2011, 2012, 2013,
                                        2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        'AZERBAIJAN', 'BELGIUM', 'BRITAIN', 'CROATIA', 'CZECH', 'DENMARK', 'ESTONIA',
                                        'FINLAND', 'FRANCE', 'GERMANY', 'GREECE', 'HUNGARY', 'ICELAND', 'IRELAND',
                                        'ITALY', 'LUXEMBOURG', 'NETHERLANDS', 'NORWAY', 'POLAND', 'PORTUGAL',
                                        'RUSSIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'TURKEY',
                                        'UKRAINE'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print(
            'Main result for full regression of hypothesis 2 with yearly credit rating changes as dependent variable ...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

    def h1_size_impact(self):
        """
        Re-run full regression as in h1_refinitiv() but breaking the sample into top 25% and bottom 25% quantile.

        Reason for repetition:
            - some dummies are redundant after slicing data and hence column names used in the regression will be changed.
            - lose some observations: affect the categorical dependent variable, which is generated based on the dataset

        Regression results are printed out in the console and used to report data in Appendix F of the thesis.
        """
        data = self.regression_data_dict['h1_refinitiv'].copy(deep=True)

        #
        # top 25% quantile
        #
        # quartile check for big companies
        sub_data1 = data.loc[data['SIZE'] >= data['SIZE'].quantile(q=0.75)].copy(deep=True)
        sub_data1 = sub_data1.loc[:, (sub_data1 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data1[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data1[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data1[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        'DENMARK', 'FRANCE', 'GERMANY', 'ITALY', 'LUXEMBOURG',
                                        'NETHERLANDS', 'NORWAY', 'RUSSIA', 'SPAIN'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using Refinitiv dataset with top 25% quantile...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)

        #
        # bottom 25% quantile
        #
        # quartile check for big companies
        sub_data2 = data.loc[data['SIZE'] <= data['SIZE'].quantile(q=0.25)].copy(deep=True)
        sub_data2 = sub_data2.loc[:, (sub_data2 != 0).any(axis=0)]  # remove redundant dummies

        # convert dependent variable to categorical type (as required to run ordered logistic regression)
        change_type = CategoricalDtype(
            categories=sorted(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG].unique()), ordered=True)
        sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG] = sub_data2[
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG].astype(change_type)

        # ordered logistic regression
        full_mod_log = OrderedModel(sub_data2[Variables.RegressionData.DependentVar.H1_CREDIT_RTG],
                                    sub_data2[[
                                        Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                                        Variables.RegressionData.ControlVar.H1_SIZE,
                                        Variables.RegressionData.ControlVar.H1_LEV,
                                        Variables.RegressionData.ControlVar.H1_ICOV,
                                        Variables.RegressionData.ControlVar.H1_OMAR,
                                        2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                        'Energy and Natural Resources', 'Utility',
                                        'BELGIUM', 'BRITAIN', 'FINLAND', 'FRANCE', 'GERMANY', 'IRELAND', 'ITALY',
                                        'LUXEMBOURG',
                                        'NORWAY', 'POLAND', 'PORTUGAL', 'RUSSIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND',
                                        'TURKEY'
                                    ]],
                                    distr='logit')
        res_log = full_mod_log.fit(method='bfgs')
        print('Main result for full regression of hypothesis 1 using Refinitiv dataset with bottom 25% quantile...')
        print(res_log.summary())
        print('Pseudo R squared of the regression is: ')
        print(res_log.prsquared)


if __name__ == "__main__":
    Regression().control(mode='main')
    pass
