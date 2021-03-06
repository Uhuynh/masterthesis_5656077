import os
import pandas as pd


class Helper:

    @staticmethod
    def get_data():
        """Generate ISIN_to_download file"""
        cwd = os.path.dirname(os.path.abspath(__file__))
        bvd_fund = pd.read_stata(cwd + '\\BvD_fundamentals.dta')
        gvkey = pd.read_stata(cwd + '\\Identifiers_GVKEY.dta')
        isin = pd.read_stata(cwd + '\\Identifiers_ISIN.dta')
        company_id = pd.read_stata(cwd + '\\Company_ID_v02_ISSUER_P_UP_FFM_12032018.dta')
        ffm_fundamental = pd.read_stata(cwd + '\\FFM_fundamentals_qtrly.dta')

        corp_rating = pd.read_stata(cwd + '\\CorporateRatings_since_1980.dta')
        corp_rating_unclear = pd.read_csv(cwd + '\\European Corporations - S&P Ratings since 1980.csv')
        corp_rating_unclear = corp_rating_unclear.rename(columns={'ORG_ID': 'org_id'})
        corp_rating_master = corp_rating.merge(corp_rating_unclear[['org_id', 'INDUSTRY', 'COUNTRY']], on='org_id', how='left')

        corp_rating_master_filter = corp_rating_master.loc[corp_rating_master['INDUSTRY'].notnull()]
        corp_rating_master_filter = corp_rating_master_filter.drop_duplicates(subset=['companyid'], keep='last')
        final = corp_rating_master_filter.merge(isin, on='companyid', how='left')
        export = final.drop(columns=['rating_date', 'rat', 'rating', 'companyname_y'])
        export = export.loc[export['isin'].notnull()]

        with pd.ExcelWriter('ISIN_to_download' + '.xlsx') as writer:
            export.to_excel(writer, sheet_name='ISIN_to_download', index=False)

        return cwd


Helper.get_data()
