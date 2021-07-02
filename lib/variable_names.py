class Variables:
    """
    Contains variables and file names that are frequently re-used within the project.

    Reason for this class: if we want to change / add a variable, we only need to do
    once within this class, which helps us avoid using literal strings repeatedly
    in many places.
    """

    class BloombergDB:
        """
        File names of raw data as well as common mnemonic field names
        downloaded from Bloomberg Terminal database.
        """

        class FILES:

            RAW_DATA_FILE_NAME = 'bloomberg_raw.xlsx'
            ESG_SHEET_NAME = 'esg'
            COMPANY_INFO_SHEET_NAME = 'company_info'
            SP_RATING_CHANGES_SHEET_NAME = 'sp_rating_changes'
            ACCOUNTING_DATA_SHEET_NAME = 'accounting'

        class FIELDS:

            BB_TICKER = 'BB_TICKER'


    class RefinitivDB:
        """
        File names of raw data downloaded from Refinitiv DataStream.
        """

        RAW_DATA_FILE_NAME = 'refinitiv_raw.xlsx'
        ESG_SHEET_NAME = 'esg'


    class SupervisorData:
        """
        File names of raw data received from supervisor (Ms. Zorka),
        which includes data about S&P credit ratings of European firms
        from 1980 to 2015.
        """

        FILE_NAME = 'credit_rating_supervisors.xlsx'
        SHEET_NAME = 'credit_rating'


    class RefinitivESG:
        """
        ESG fields mnemonic of Refinitiv.
        """

        GOV = 'CGSCORE'
        ENV = 'ENSCORE'
        SOCIAL = 'SOSCORE'
        TOTAL = 'TRESGS'


    class SPGlobalESG:
        """
        ESG fields mnemonic of S&P Global (formerly RobecoSAM).
        """

        ECON = 'ROBECOSAM_ECON_DIMENSION_RANK'
        ENV = 'ROBECOSAM_ENV_DIMENSION_RANK'
        SOCIAL = 'ROBECOSAM_SOCIAL_DIMENSION_RANK'
        TOTAL = 'ROBECOSAM_TOTAL_STBLY_RANK'


    class SustainalyticsESG:
        """
        ESG fields mnemonic of Sustainalytics.
        """

        ENV = 'SUSTAINALYTICS_ENVIRONMENT_PCT'
        GOV = 'SUSTAINALYTICS_GOVERNANCE_PCT'
        SOCIAL = 'SUSTAINALYTICS_SOCIAL_PERCENTILE'
        TOTAL = 'SUSTAINALYTICS_RANK'


    class SPCreditRtg:
        """
        Fields mnemonic of S&P credit ratings.
        """

        LT_LOCAL_ISSUER = 'LT Local Issuer Credit'


    class CleanedData:
        """
        File names of cleaned data.
        """

        FILE_NAME = 'cleaned_data.xlsx'
        BLOOMBERG_ESG_SHEET_NAME = 'esg_bb'
        REFINITIV_ESG_SHEET_NAME = 'esg_refinitiv'
        SP_CREDIT_RTG_SHEET_NAME = 'sp_credit_rtg'
        POPULATED_SP_CREDIT_RTG_SHEET_NAME = 'populated_sp_credit_rtg'
        ACCOUNTING_SHEET_NAME = 'accounting'
        POPULATED_ACCOUNTING_SHEET_NAME = 'populated_accounting'

    class DescriptiveStats:
        """
        File names of descriptive statistics
        """

        FILE_NAME = 'descriptive_stats.xlsx'
        DESCRIPTIVE_STATS_SHEET_NAME = 'descriptive_stats'
        CORR_H1_REFINITIV_SHEET_NAME = 'corr_h1_refinitiv'
        CORR_H1_SPGLOBAL_SHEET_NAME = 'corr_h1_spglobal'
        CORR_H1_SUSTAINALYTICS_SHEET_NAME = 'corr_h1_sustainalytics'
        CORR_H2_SHEET_NAME = 'corr_h2'
        CORR_ESG_SHEET_NAME = 'corr_esg'


    class RegressionData:
        """
        File and variables names (of both hypotheses) that will be used in the regression.
        """

        class INDUSTRY:
            """
            Fields mnemonic of three chosen industries in the sample.
            """
            INDUSTRY_1 = 'Aerospace/Automotive/Capital Goods/Metal'
            INDUSTRY_2 = 'Energy and Natural Resources'
            INDUSTRY_3 = 'Utility'

        class FILES:
            """
            File names (of both hypotheses) that will be used in the regression.
            """

            # H1 file names
            H1_FILE_NAME = 'h1_regression_data.xlsx'
            H1_SUSTAINALYTICS_SHEET_NAME = 'h1_sustainalytics'
            H1_REFINITIV_SHEET_NAME = 'h1_refinitiv'
            H1_SPGLOBAL_SHEET_NAME = 'h1_spglobal'

            # H2 file names
            H2_FILE_NAME = 'h2_regression_data.xlsx'
            H2_MONTHLY_DATA_SHEET_NAME = 'h2_monthly'
            H2_YEARLY_DATA_SHEET_NAME = 'h2_yearly'
            H2_MAIN_DATA_SHEET_NAME = 'h2_main'

        class DependentVar:
            """
            Names of dependent variables (of both hypotheses) that will be used in the regression.
                - H1: hypothesis 1
                - H2: hypothesis 2
            """

            H1_CREDIT_RTG = 'CREDIT_RTG'
            H2_CREDIT_RTG_CHANGE = 'CR_CHANGE'
            H2_MONTHLY_CREDIT_RTG_CHANGE = 'CR_CHANGE_M'
            H2_YEARLY_CREDIT_RTG_CHANGE = 'CR_CHANGE_Y'

        class IndependentVar:
            """
            Names of independent variables (of both hypotheses) that will be used in the regression.
                - H1: hypothesis 1
                - H2: hypothesis 2
            """

            H1_ESG_RTG = 'ESG_RTG'
            H1_ESG_ENV = 'ESG_E'
            H1_ESG_SOC = 'ESG_S'
            H1_ESG_GOV = 'ESG_G'

            H2_ESG_RATED_DUMMY = 'ESG_RATED'

        class ControlVar:
            """
            Fields mnemonic of control variables (of both hypotheses) that will be used in the regression
                - H1: hypothesis 1
                - H2: hypothesis 2
            """

            H1_SIZE = 'SIZE'
            H1_LEV = 'LEVERAGE'
            H1_ICOV = 'INTEREST_COVERAGE_RATIO'
            H1_OMAR = 'OPER_MARGIN'

            H2_AVG_SIZE = 'AVG_SIZE'
            H2_AVG_LEV = 'AVG_LEV'
            H2_AVG_ICOV = 'AVG_ICOV'
            H2_AVG_OMAR = 'AVG_OMAR'
            H2_LONG_TERM_DUMMY = 'LONG_TERM'
