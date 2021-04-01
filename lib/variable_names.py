
class Variables:
    """
    Contains variable names that are frequently re-used within the project.
    """

    class Bloomberg:

        FILE_NAME = 'bloomberg_raw.xlsx'
        ESG_SHEET_NAME = 'esg'
        COMPANY_INFO_SHEET_NAME = 'company_info'
        SP_RATING_CHANGES_SHEET_NAME = 'sp_rating_changes'
        BB_TICKER = 'BB_TICKER'



    class Refinitiv:

        FILE_NAME = 'refinitiv_raw.xlsx'
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

        LT_FOREIGN_ISSUER = 'LT Foreign Issuer Credit'


    class CleanedData:

        FILE_NAME = 'cleaned_data.xlsx'
        BLOOMBERG_ESG_SHEET_NAME = 'esg_bb'
        REFINITIV_ESG_SHEET_NAME = 'esg_refinitiv'
        SP_CREDIT_RTG_SHEET_NAME = 'sp_credit_rtg'
        POPULATED_SP_CREDIT_RTG_SHEET_NAME = 'populated_sp_credit_rtg'
