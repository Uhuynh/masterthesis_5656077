import os
import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import itertools

from lib.variable_names import Variables
from lib.helpers import ExtractData, DataRoot

"""
This module performs analyzing process for regression data.
More details can be found in the documentation of the class below.

To execute the module simply click the run button.
"""


class AnalyseData(DataRoot):
    """
    This class provides different methods for analyzing regression data.
    """
    def __init__(self):
        super().__init__()
        self.regression_data_dict = ExtractData().extract_regression_data()

    def control(self) -> None:
        """
        The following steps are done:
            - get descriptive statistics of all datasets for both hypotheses
            - get correlation matrices of all datasets for both hypotheses
            - save all data generated above to excel
            - generate pair plots
        """
        # get descriptive statistics of all datasets
        descriptive_stat = self.descriptive_stat()

        # get correlation matrix of each dataset of hypothesis 1
        corr_h1_refinitiv = self.corr_h1(data_set='h1_refinitiv')
        corr_h1_spglobal = self.corr_h1(data_set='h1_spglobal')
        corr_h1_sustainalytics = self.corr_h1(data_set='h1_sustainalytics')

        # get correlation matrix of hypothesis 2
        corr_h2 = self.corr_h2(data=self.regression_data_dict['h2_main'])

        # get correlation matrix of ESG scores using common sample
        corr_esg = self.corr_esg_ratings_common_sample()

        # export all generated data to Excel file saved under 'data/descriptive stats/descriptive_stats.xlsx'
        with pd.ExcelWriter(os.path.join(self.descriptive_stats_root, Variables.DescriptiveStats.FILE_NAME)) as writer:
            descriptive_stat.to_excel(writer, sheet_name=Variables.DescriptiveStats.DESCRIPTIVE_STATS_SHEET_NAME, index=False)
            corr_h1_refinitiv.to_excel(writer, sheet_name=Variables.DescriptiveStats.CORR_H1_REFINITIV_SHEET_NAME, index=False)
            corr_h1_spglobal.to_excel(writer, sheet_name=Variables.DescriptiveStats.CORR_H1_SPGLOBAL_SHEET_NAME, index=False)
            corr_h1_sustainalytics.to_excel(writer, sheet_name=Variables.DescriptiveStats.CORR_H1_SUSTAINALYTICS_SHEET_NAME, index=False)
            corr_h2.to_excel(writer, sheet_name=Variables.DescriptiveStats.CORR_H2_SHEET_NAME, index=False)
            corr_esg.to_excel(writer, sheet_name=Variables.DescriptiveStats.CORR_ESG_SHEET_NAME, index=False)

        # generate pair plots
        self.pairplot(data_set='h1_refinitiv')
        self.pairplot(data_set='h1_spglobal')
        self.pairplot(data_set='h1_sustainalytics')
        self.pairplot(data_set='h2_main')

    def descriptive_stat(self) -> pd.DataFrame:
        """
        Returns a dataframe of descriptive statistics for each regression dataset
        that is retrieved and stored in the class variable 'regression_data_dict'.

        The data is used for Table 4 in the thesis.
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

    def corr_h1(self, data_set='h1_refinitiv') -> pd.DataFrame:
        """
        :parameter data_set: str (choices are 'h1_refinitiv', 'h1_spglobal', and 'h1_sustainalytics')

        This function generates Pearson pairwise correlation coefficients and p-values
        for all variables used in each dataset of the regression of hypothesis 1:
            - pairwise combinations are generated by using itertools package
            - scipy library is used to calculate Pearson pairwise correlation and two-sided p-values,
              for more info regarding the library:
              https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html

        The generated data is used to report table 5 in the thesis.

        :return result: a data frame contains all generated information
        """

        data = self.regression_data_dict[data_set]

        # get all variables' names used in regression of hypothesis 1
        all_var = [
            Variables.RegressionData.DependentVar.H1_CREDIT_RTG,
            Variables.RegressionData.IndependentVar.H1_ESG_RTG,
            Variables.RegressionData.IndependentVar.H1_ESG_ENV,
            Variables.RegressionData.IndependentVar.H1_ESG_SOC,
            Variables.RegressionData.IndependentVar.H1_ESG_GOV,
            Variables.RegressionData.ControlVar.H1_SIZE,
            Variables.RegressionData.ControlVar.H1_LEV,
            Variables.RegressionData.ControlVar.H1_ICOV,
            Variables.RegressionData.ControlVar.H1_OMAR
        ]

        # create all subsets of all_var with exactly 2 elements
        all_var_subset = set(itertools.combinations(all_var, 2))

        # calculate correlation coefficients and p-values of each subset
        result = []
        for _, element in enumerate(all_var_subset):
            data_dict = {
                'variable1': element[0],
                'variable2': element[1],
                'corr_coeff': stats.pearsonr(data[element[0]], data[element[1]])[0],
                'p_value': stats.pearsonr(data[element[0]], data[element[1]])[1],
                'dataset': data_set,
            }
            df_summary = pd.DataFrame.from_dict([data_dict])
            result.append(df_summary)
        result = pd.concat(result)
        result = result.reset_index(drop=True)

        return result


    @staticmethod
    def corr_h2(data) -> pd.DataFrame:
        """
        This function generates pairwise correlation coefficients and p-values for hypothesis 2.
            - pairwise combinations are generated by using itertools package
            - scipy library is used to calculate Pearson pairwise correlation and two-sided p-values,
            for more info regarding the library:
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html

        The generated data is used to report table 5 in the thesis.

        :return result: a data frame contains all generated information
        """

        # get all variables' names used in regression of hypothesis 2
        all_var = [
            Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE,
            Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
            Variables.RegressionData.ControlVar.H2_AVG_SIZE,
            Variables.RegressionData.ControlVar.H2_AVG_LEV,
            Variables.RegressionData.ControlVar.H2_AVG_ICOV,
            Variables.RegressionData.ControlVar.H2_AVG_OMAR,
            Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
        ]

        # create all subsets of all_var with exactly 2 elements
        all_var_subset = set(itertools.combinations(all_var, 2))

        # calculate correlation coefficients and p-values of each subset
        result = []
        for _, element in enumerate(all_var_subset):
            data_dict = {
                'variable1': element[0],
                'variable2': element[1],
                'corr_coeff': stats.pearsonr(data[element[0]], data[element[1]])[0],
                'p_value': stats.pearsonr(data[element[0]], data[element[1]])[1],
            }
            df_summary = pd.DataFrame.from_dict([data_dict])
            result.append(df_summary)
        result = pd.concat(result)
        result = result.reset_index(drop=True)

        return result

    def corr_esg_ratings_common_sample(self):
        """
        This functions calculates correlation coefficients and p-values for three chosen ESG ratings using
        common sample.
        """
        # common sample to calculate ESG ratings correlation
        data = self.regression_data_dict['h2_monthly']
        common_sample = data.loc[
            (data[Variables.RefinitivESG.TOTAL].notnull()) &
            (data[Variables.SPGlobalESG.TOTAL].notnull()) &
            (data[Variables.SustainalyticsESG.TOTAL].notnull())
            ]

        all_var = [
            Variables.RefinitivESG.TOTAL,
            Variables.SPGlobalESG.TOTAL,
            Variables.SustainalyticsESG.TOTAL
        ]

        # create all subsets of all_var with exactly 2 elements
        all_var_subset = set(itertools.combinations(all_var, 2))

        # calculate correlation coefficients and p-values of each subset
        result = []
        for _, element in enumerate(all_var_subset):
            data_dict = {
                'variable1': element[0],
                'variable2': element[1],
                'corr_coeff': stats.pearsonr(common_sample[element[0]], common_sample[element[1]])[0],
                'p_value': stats.pearsonr(common_sample[element[0]], common_sample[element[1]])[1],
            }
            df_summary = pd.DataFrame.from_dict([data_dict])
            result.append(df_summary)
        result = pd.concat(result)
        result = result.reset_index(drop=True)

        return result

    def pairplot(self, data_set='h1_refinitiv'):
        """
        :parameter data_set: data_set: str (choices are 'h1_refinitiv', 'h1_spglobal', 'h1_sustainalytics', and 'h2_main')

        Plotting histogram and scatter plots of regression variables using seaborn package.
        For more information: https://seaborn.pydata.org/generated/seaborn.pairplot.html

        The generated plots are used in Appendix A of the thesis.
        """
        # get dataset to be used:
        data = self.regression_data_dict[data_set]

        # get variables to be used, depending on chosen dataset
        if data_set == 'h2_main':  # hypothesis 2's regression variables
            all_var = [
                Variables.RegressionData.DependentVar.H2_CREDIT_RTG_CHANGE,
                Variables.RegressionData.IndependentVar.H2_ESG_RATED_DUMMY,
                Variables.RegressionData.ControlVar.H2_AVG_SIZE,
                Variables.RegressionData.ControlVar.H2_AVG_LEV,
                Variables.RegressionData.ControlVar.H2_AVG_ICOV,
                Variables.RegressionData.ControlVar.H2_AVG_OMAR,
                Variables.RegressionData.ControlVar.H2_LONG_TERM_DUMMY,
            ]
        else:  # hypothesis 1's regression variables
            all_var = [
                Variables.RegressionData.DependentVar.H1_CREDIT_RTG,
                Variables.RegressionData.IndependentVar.H1_ESG_RTG,
                # Variables.RegressionData.IndependentVar.H1_ESG_ENV,
                # Variables.RegressionData.IndependentVar.H1_ESG_SOC,
                # Variables.RegressionData.IndependentVar.H1_ESG_GOV,
                Variables.RegressionData.ControlVar.H1_SIZE,
                Variables.RegressionData.ControlVar.H1_LEV,
                Variables.RegressionData.ControlVar.H1_ICOV,
                Variables.RegressionData.ControlVar.H1_OMAR
            ]

        plt.figure(figsize=(20, 20))
        sns.pairplot(data, vars=all_var, corner=True, height=2, aspect=1)
        plt.show()


if __name__ == "__main__":
    AnalyseData().control()
