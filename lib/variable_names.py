class Variables:
    """
    Contains variables and file names that are frequently re-used within the project.
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

        FILE_NAME = 'credit_rating_Zorka.xlsx'
        SHEET_NAME = 'credit_rating_Zorka'


    class RefinitivESG:

        GOV = 'CGSCORE'
        ENV = 'ENSCORE'
        SOCIAL = 'SOSCORE'
        TOTAL = 'TRESGS'


    class SPGlobalESG:

        ECON = 'ROBECOSAM_ECON_DIMENSION_RANK'
        ENV = 'ROBECOSAM_ENV_DIMENSION_RANK'
        SOCIAL = 'ROBECOSAM_SOCIAL_DIMENSION_RANK'
        TOTAL = 'ROBECOSAM_TOTAL_STBLY_RANK'


    class SustainalyticsESG:

        ENV = 'SUSTAINALYTICS_ENVIRONMENT_PCT'
        GOV = 'SUSTAINALYTICS_GOVERNANCE_PCT'
        SOCIAL = 'SUSTAINALYTICS_SOCIAL_PERCENTILE'
        TOTAL = 'SUSTAINALYTICS_RANK'


    class SPCreditRtg:

        LT_LOCAL_ISSUER = 'LT Local Issuer Credit'


    class ControlVar:

        SIZE = 'SIZE'
        LEV = 'LEVERAGE'
        ICOV = 'INTEREST_COVERAGE_RATIO'
        OMAR = 'OPER_MARGIN'


    class CleanedData:

        FILE_NAME = 'cleaned_data.xlsx'
        BLOOMBERG_ESG_SHEET_NAME = 'esg_bb'
        REFINITIV_ESG_SHEET_NAME = 'esg_refinitiv'
        SP_CREDIT_RTG_SHEET_NAME = 'sp_credit_rtg'
        POPULATED_SP_CREDIT_RTG_SHEET_NAME = 'populated_sp_credit_rtg'
        ACCOUNTING_SHEET_NAME = 'accounting'
        POPULATED_ACCOUNTING_SHEET_NAME = 'populated_accounting'


    class RegressionData:

        # Industries
        INDUSTRY_1 = 'Aerospace/Automotive/Capital Goods/Metal'
        INDUSTRY_2 = 'Energy and Natural Resources'
        INDUSTRY_3 = 'Utility'

        # H1 file names
        H1_FILE_NAME = 'h1_regression_data.xlsx'
        H1_WINSORIZED_FILE_NAME = 'h1_regression_data_winsorized.xlsx'
        H1_SUSTAINALYTICS_SHEET_NAME = 'h1_sustainalytics'
        H1_REFINITIV_SHEET_NAME = 'h1_refinitiv'
        H1_SPGLOBAL_SHEET_NAME = 'h1_spglobal'

        # H2 file names
        H2_FILE_NAME = 'h2_regression_data.xlsx'

        # hypothesis 1 regression variables
        H1_ESG_RTG_VAR = 'ESG_RTG'
        H1_ESG_ENV_VAR = 'ESG_E'
        H1_ESG_SOC_VAR = 'ESG_S'
        H1_ESG_GOV_VAR = 'ESG_G'
        H1_CREDIT_RTG_VAR = 'CREDIT_RTG'

        # hypothesis 2 regression variables
        H2_CREDIT_RTG_CHANGE_VAR = 'CR_CHANGE'
        H2_ESG_RATED_DUMMY = 'ESG_RATED'
        H2_AVG_SIZE_VAR = 'AVG_SIZE'
        H2_AVG_LEV_VAR = 'AVG_LEV'
        H2_AVG_ICOV_VAR = 'AVG_ICOV'
        H2_AVG_OMAR_VAR = 'AVG_OMAR'
        H2_LONG_TERM_DUMMY = 'LONG_TERM'

        # h2 alternative model regression variables
        H2_CREDIT_RTG_YEARLY_CHANGE_VAR = 'CR_CHANGE_YEARLY'
