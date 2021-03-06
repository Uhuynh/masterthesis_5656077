import os
import pandas as pd
from datetime import date


class Helper:

    @staticmethod
    def get_company_list():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        # data part 1
        data1 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'), sheet_name=1)
        data1 = data1.drop(columns=['isin', 'startdate', 'enddate'])
        data1 = data1.drop_duplicates(keep='first')

        # data part 2
        data2 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'), sheet_name='Extra companies')
        data2 = data2[['companyname', 'bloomberg_fundamental_ticker']]

        # original data
        data = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'), sheet_name='ISIN_to_download')
        data = data.drop(columns=['isin', 'startdate', 'enddate'])
        data = data.drop_duplicates(keep='first')

        # merge data part 2 to data
        data2 = data2.merge(data, on='companyname', how='left')

        # append data2 to data1
        final = data1.append(data2, ignore_index=True)
        final = final.reset_index(drop=True)

        company_downloaded = final.iloc[:348, :]
        company_not_downloaded = final.iloc[348:, :]

        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            company_downloaded.to_excel(writer, sheet_name='company_downloaded', index=False)
            company_not_downloaded.to_excel(writer, sheet_name='company_not_downloaded', index=False)

        company_downloaded = pd.read_excel(os.path.join(data_root, 'company_list.xlsx'),
                                           sheet_name='company_downloaded')
        company_downloaded = company_downloaded.drop(columns=['bloomberg_id_isin'])
        len(company_downloaded['companyname'].unique())
        company_downloaded['check_duplication'] = company_downloaded['companyname'].duplicated(keep='last')
        company_downloaded = company_downloaded.loc[company_downloaded['check_duplication'] == False]

        test = company_not_downloaded.merge(company_downloaded, on='companyname', how='left')
        company_not_downloaded = test.loc[test['INDUSTRY_y'].notnull()]

        with pd.ExcelWriter('company_list' + '.xlsx') as writer:
            company_downloaded.to_excel(writer, sheet_name='company_downloaded', index=False)
            company_not_downloaded.to_excel(writer, sheet_name='company_not_downloaded', index=False)

        return data1

    @staticmethod
    def get_esg_data_part1():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        part1 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'),
                              sheet_name='Sustainalytics Overall Score')
        part1 = part1.rename(columns=part1.iloc[2])
        part1 = part1.iloc[4:, :]
        part1 = part1.reset_index(drop=True)

        # test reshaping data
        part1 = part1.rename(columns={part1.columns[0]: 'Dates'})
        part1 = part1.set_index('Dates')
        test = part1.unstack()
        test = test.reset_index()
        test = test.rename(columns=test.iloc[0])
        test = test.loc[test['Dates'] != 'Dates']
        test = test.reset_index(drop=True)
        test['Dates'] = pd.to_datetime(test['Dates'])
        test['Dates'] = test['Dates'].dt.date

        # loc data starting from 28-02-2014
        test = test.loc[test['Dates'] >= date(2014, 2, 28)]

        count = test.loc[test['SUSTAINALYTICS_RANK'].notnull()]
        count_no_data = test.loc[test['SUSTAINALYTICS_RANK'].isnull()]
        company_has_data = pd.DataFrame({
            'company_has_data': list(count['ASSAB SS EQUITY'].unique()),
        })

        company_no_data = pd.DataFrame({
            'company_has_no_data': list(count_no_data['ASSAB SS EQUITY'].unique()),
        })

        with pd.ExcelWriter('cleaned_data' + '.xlsx') as writer:
            test.to_excel(writer, sheet_name='part1', index=False)
            company_has_data.to_excel(writer, sheet_name='company_has_data', index=False)
            company_no_data.to_excel(writer, sheet_name='company_no_data', index=False)

    @staticmethod
    def get_esg_data_part2():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        part2 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'),
                              sheet_name='Sustainalytics 3 Pillars Score')
        part2.iloc[2, :] = part2.iloc[2, :].fillna(method='ffill', axis=0)
        part2 = part2.rename(columns=part2.iloc[2])
        part2 = part2.iloc[4:, :]
        part2 = part2.reset_index(drop=True)

        # reshape data
        part2 = part2.rename(columns={part2.columns[0]: 'Dates'})
        part2 = part2.set_index('Dates')
        part2 = part2.iloc[:180, :]

        test = part2.T
        test = test.set_index(['Dates'], append=True)
        test = test.reset_index()
        test = test.rename(columns={test.columns[0]: 'companyname', test.columns[1]: 'variable'})

        final = test.melt(id_vars=['companyname', 'variable'], var_name='Dates')
        final = pd.pivot_table(final, values='value', index=['companyname', 'Dates'], columns=['variable'],
                               aggfunc='first')
        final = final.reset_index()
        final = final.rename(columns={final.columns[0]: 'companyname', final.columns[1]: 'Dates'})
        final['Dates'] = pd.to_datetime(final['Dates'])
        final['Dates'] = final['Dates'].dt.date

        len(final['companyname'].unique())

        part1 = pd.read_excel(os.path.join(data_root, 'cleaned_data.xlsx'), sheet_name='part1')
        part1['Dates'] = part1['Dates'].dt.date
        new = pd.merge(part1, final, how='left', left_on=['ASSAB SS EQUITY', 'Dates'],
                       right_on=['companyname', 'Dates'])

        with pd.ExcelWriter('cleaned_data2' + '.xlsx') as writer:
            new.to_excel(writer, sheet_name='part1&2', index=False)

        return final

    @staticmethod
    def get_esg_data_part3():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        part2 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'),
                              sheet_name='S&P Score')
        part2.iloc[3, :] = part2.iloc[3, :].fillna(method='ffill', axis=0)
        part2 = part2.rename(columns=part2.iloc[3])
        part2 = part2.iloc[5:, :]
        part2 = part2.reset_index(drop=True)

        # reshape data
        part2 = part2.rename(columns={part2.columns[0]: 'Dates'})
        part2 = part2.set_index('Dates')
        # part2 = part2.iloc[:180, :]

        test = part2.T
        test = test.set_index(['Dates'], append=True)
        test = test.reset_index()
        test = test.rename(columns={test.columns[0]: 'companyname', test.columns[1]: 'variable'})

        final = test.melt(id_vars=['companyname', 'variable'], var_name='Dates')
        final = pd.pivot_table(final, values='value', index=['companyname', 'Dates'], columns=['variable'],
                               aggfunc='first')
        final = final.reset_index()
        final = final.rename(columns={final.columns[0]: 'companyname', final.columns[1]: 'Dates'})
        final['Dates'] = pd.to_datetime(final['Dates'])
        final['Dates'] = final['Dates'].dt.date

        len(final['companyname'].unique())

        count_data = final.loc[final['ROBECOSAM_TOTAL_STBLY_RANK'].notnull()]
        count_no_data = final.loc[final['ROBECOSAM_TOTAL_STBLY_RANK'].isnull()]
        company_has_data = pd.DataFrame({
            'company_has_data': list(count_data['companyname'].unique()),
        })

        company_no_data = pd.DataFrame({
            'company_has_no_data': list(count_no_data['companyname'].unique()),
        })

        part1 = pd.read_excel(os.path.join(data_root, 'cleaned_data2.xlsx'), sheet_name='part1&2')
        part1['Dates'] = pd.to_datetime(part1['Dates'])
        part1['Dates'] = part1['Dates'].dt.date
        new = pd.merge(part1, final, how='outer', left_on=['companyname', 'Dates'],
                       right_on=['companyname', 'Dates'])

        with pd.ExcelWriter('cleaned_data' + '.xlsx') as writer:
            new.to_excel(writer, sheet_name='all', index=False)
            company_has_data.to_excel(writer, sheet_name='company_has_data_robeco', index=False)
            company_no_data.to_excel(writer, sheet_name='company_no_data_robeco', index=False)

        return final

    @staticmethod
    def get_esg_data_extra():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        part2 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'),
                              sheet_name='extra esg part 1')
        # part2.iloc[3, :] = part2.iloc[3, :].fillna(method='ffill', axis=0)
        part2 = part2.rename(columns=part2.iloc[0])
        part2 = part2.iloc[1:, :]
        # part2 = part2.reset_index(drop=True)

        # reshape data
        part2 = part2.rename(columns={part2.columns[0]: 'Dates'})
        part2 = part2.set_index('Dates')
        # part2 = part2.iloc[:180, :]

        test = part2.T
        test = test.rename(columns={test.columns[0]: 'variable'})
        test = test.set_index(['variable'], append=True)
        test = test.reset_index()
        test = test.rename(columns={test.columns[0]: 'companyname'})

        final = test.melt(id_vars=['companyname', 'variable'], var_name='Dates')
        final = pd.pivot_table(final, values='value', index=['companyname', 'Dates'], columns=['variable'],
                               aggfunc='first')
        final = final.reset_index()
        final = final.rename(columns={final.columns[0]: 'companyname', final.columns[1]: 'Dates'})
        final['Dates'] = pd.to_datetime(final['Dates'])
        final['Dates'] = final['Dates'].dt.date


        len(final['companyname'].unique())

        part1 = pd.read_excel(os.path.join(data_root, 'cleaned_data2.xlsx'), sheet_name='part1&2')
        part1['Dates'] = pd.to_datetime(part1['Dates'])
        part1['Dates'] = part1['Dates'].dt.date
        new = pd.merge(part1, final, how='outer', left_on=['companyname', 'Dates'],
                       right_on=['companyname', 'Dates'])

        with pd.ExcelWriter('cleaned_data' + '.xlsx') as writer:
            new.to_excel(writer, sheet_name='all', index=False)

        return final

    @staticmethod
    def get_accounting_data():
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_root = os.path.join(project_root, 'data')

        part2 = pd.read_excel(os.path.join(data_root, 'ISIN_to_download.xlsx'),
                              sheet_name='Accounting Data')
        part2.iloc[2, :] = part2.iloc[2, :].fillna(method='ffill', axis=0)
        part2 = part2.rename(columns=part2.iloc[2])
        part2 = part2.iloc[4:, :]
        part2 = part2.reset_index(drop=True)

        # reshape data
        part2 = part2.rename(columns={part2.columns[0]: 'Dates'})
        part2 = part2.set_index('Dates')
        # part2 = part2.iloc[:180, :]

        test = part2.T
        test = test.set_index(['Dates'], append=True)
        test = test.reset_index()
        test = test.rename(columns={test.columns[0]: 'companyname', test.columns[1]: 'variable'})

        final = test.melt(id_vars=['companyname', 'variable'], var_name='Dates')
        final = pd.pivot_table(final, values='value', index=['companyname', 'Dates'], columns=['variable'],
                               aggfunc='first')
        final = final.reset_index()
        final = final.rename(columns={final.columns[0]: 'companyname', final.columns[1]: 'Dates'})
        final['Dates'] = pd.to_datetime(final['Dates'])
        final['Dates'] = final['Dates'].dt.date

        len(final['companyname'].unique())

        with pd.ExcelWriter('cleaned_data2' + '.xlsx') as writer:
            final.to_excel(writer, sheet_name='accounting data', index=False)

        return final

Helper.get_accounting_data()
