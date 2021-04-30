
class Variables:
    """
    Contains variable names that are frequently re-used within the project.
    """

    class Bloomberg:

        RAW_DATA_FILE_NAME = 'bloomberg_raw.xlsx'
        ESG_SHEET_NAME = 'esg'
        COMPANY_INFO_SHEET_NAME = 'company_info'
        SP_RATING_CHANGES_SHEET_NAME = 'sp_rating_changes'
        ACCOUNTING_SHEET_NAME = 'accounting'
        BB_TICKER = 'BB_TICKER'


    class Refinitiv:

        RAW_DATA_FILE_NAME = 'refinitiv_raw.xlsx'
        ESG_SHEET_NAME = 'esg'


    class SupervisorData:

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
        LVG = 'LEVERAGE'
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

        FILE_NAME = 'regression_data.xlsx'
        H1_SUSTAINALYTICS_SHEET_NAME = 'h1_sustainalytics'
        H1_REFINITIV_SHEET_NAME = 'h1_refinitiv'
        H1_SPGLOBAL_SHEET_NAME = 'h1_spglobal'
        H2_SHEET_NAME = 'h2'

        ESG_RTG_VAR = 'ESG_RTG'
        ESG_ENV_VAR = 'ESG_E'
        ESG_SOC_VAR = 'ESG_S'
        ESG_GOV_VAR = 'ESG_G'
        CREDIT_RTG_VAR = 'CREDIT_RTG'
        CREDIT_RTG_CHANGE_VAR = 'CREDIT_RTG_CHANGE'
        ESG_RATED_DUMMY = 'ESG_RATED'