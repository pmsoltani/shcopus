# modules

import csv
from collections import OrderedDict
from collections import Counter
# import requests
import sqlite3
import io
import os
from shcopus_functions import *
# obtaining & parsing scopus data

query = '' or 'Department of Materials Science and Engineering, Sharif University of Technology'

db_query_aut = 'simchi'
db_query_year1 = '' #or 2016
db_query_year2 = 2018

db_name = 'papers.db'
papers_extension = 'csv'
papers_directory = 'papers'

db = '' or sqlite3.connect(db_name)

if type(db) == sqlite3.Connection:
    db.row_factory = dict_factory
    cursor = db.cursor()
    if db_query_year1 == '':
        cursor.execute(
            '''
                SELECT * FROM papers WHERE 
                Authors LIKE ?
            ''', 
            (
                '%' + db_query_aut + '%',
            )
        )
    else:
        cursor.execute(
            '''
                SELECT * FROM papers WHERE 
                Year >= cast(? as numeric) AND 
                Year <= cast(? as numeric) AND 
                Authors LIKE ?
            ''', 
            (
                db_query_year1, db_query_year2, '%' + db_query + '%',
            )
        )
    papers = cursor.fetchall()

counter = 0
for i in papers:
    
    i['raw_countries'] = [] # gets the country name from the last piece in the address
    i['countries'] = [] # gets the country name, if it is in "selected_countries" or "islamic_countries"
    i['depts'] = []
    i['institutions'] = []
    i['sharif_only'] = True
    i['has_foreign'] = False
    i['has_islamic'] = False
    i['has_qs100'] = False
    i['has_qs300'] = False
    i['errors'] = {
        'country': {'type': 'Error', 'value': False},
        'qs': {'type': 'Error', 'value': False},
        'author': {'type': 'Warning', 'value': False, 'message': ''}
    }
    
    temp = OrderedDict()
    affils = i['affils'].split(';')
    for cnt, affil in enumerate(affils):
        temp[cnt] = affil.strip()
    i['affils'] = temp
    
    temp = OrderedDict()
    authors = i['auts'].split(',')
    for cnt, author in enumerate(authors):
        temp[cnt] = author.strip()
        
        # spliting with ('.') sometimes can cause problems. For example in J. Smith, III 
        if '.' not in author:
            print(f'Possible invalid author:\t{temp[cnt]}\ton\t{counter}')
            i['errors']['author']['value'] = True
            i['errors']['author']['message'] = f'Possible invalid author: {temp[cnt]}, on row {counter}'
    i['auts'] = temp
    
    authors_with_affil = i['auts_affils'].split(';')
    temp = OrderedDict()
    for cnt, author in enumerate(authors_with_affil):
        temp[cnt] = {
            'name_address': author.strip(),
            'sharif': False,
            'faculty': False,
            'sharif_id': '',
            'dept': '',
            'foreign': False,
            'islamic': False,
            'country': '',
            'qs100': False,
            'qs300': False,
            'query': False,
        }
        # is the author affiliated with Sharif?
        # if 'sharif' in author.lower():
        if in_list('sharif', author.lower().split(',')[2:], 'any'):
            temp[cnt]['sharif'] = True
            i['institutions'].append('Sharif University of Technology')
            
            [temp[cnt]['faculty'], temp[cnt]['sharif_id']] = in_list(
                author.lower().split(',')[0],
                [datasets['faculties'][faculty]['last'].lower() for faculty in datasets['faculties']],
                'any',
                True
            )
            if temp[cnt]['faculty']:
                temp[cnt]['sharif_id'] = list(datasets['faculties'].keys())[temp[cnt]['sharif_id']]
                temp[cnt]['dept'] = datasets['faculties'][temp[cnt]['sharif_id']]['dept']
            else:
                temp[cnt]['sharif_id'] = ''
            # if Author is from Sharif, what is his/her department?
            for element in author.split(','):
                if 'department' in element.lower() or 'institute' in element.lower():
                    element = element.strip()
                    # temp[cnt]['dept'] = element
                    if element in sharif_depts.keys():
                        # temp[cnt]['dept'] = sharif_depts[element]
                        if temp[cnt]['faculty'] and sharif_depts[element] not in temp[cnt]['dept']:
                            print(temp[cnt]['sharif_id'],temp[cnt]['dept'],author)
                            print('**************')
                        else:
                            print(temp[cnt]['sharif_id'],temp[cnt]['dept'],sharif_depts[element])
                        # temp[cnt]['faculty'] = faculty_data(temp[cnt]['dept'], datasets['faculties'], author.split(',')[0])
                        # if temp[cnt]['dept'] not in datasets['faculties'][339]['Dept'] and :
                        #     print(temp[cnt]['name_address'])
                        #     print('******************')
                        #     print('ERRRRR')
                        #     print(counter)
                        #     print(element)
                        #     print(i['doi'])
                        #     print('-/-/-/-/-/-/-/-')
                        i['depts'].append(temp[cnt]['dept'])
                        break
        else:
            i['sharif_only'] = False
            i['institutions'].append(', '.join(map(lambda element: element.strip(), author.split(',')[2:-2])))
        
        # is Author from Iran?
        if not(in_list('iran', author.lower().split(',')[2:], 'any')):
            temp[cnt]['foreign'] = True
            i['has_foreign'] = True
            
            for country in datasets['countries']:
                if country in author.lower():
                    temp[cnt]['country'] = datasets['countries'][country]['id']
                    if datasets['countries'][country]['islamic']:
                        temp[cnt]['islamic'] = True
                        i['has_islamic'] = True
                    break
        else:
            temp[cnt]['country'] = 'IR'
        i['countries'].append(temp[cnt]['country'])
        i['raw_countries'].append(author.split(',')[-1].strip())
        
        # check whether the author is affiliated with any of the top 100 or top 101-300 universities in QS ranking
        if any(uni.lower() in author.lower() for uni in datasets['qs100']):
            temp[cnt]['qs100'] = True
            i['has_qs100'] = True
            
        if any(uni.lower() in author.lower() for uni in datasets['qs300']):
            temp[cnt]['qs300'] = True
            i['has_qs300'] = True
        if temp[cnt]['qs100'] and temp[cnt]['qs300']:
            i['errors']['qs']['value'] = True
            # print(f'QS Error on row: {counter}')

        
        if query.lower() in author.lower():
            temp[cnt]['query'] = True
    
    i['auts_affils'] = temp
    
    # is the paper journal from JCR top 1% or top 25%?
    i['src'] = OrderedDict({
        'journal': i['src'], 
        'jcr_q1': False, 
        'jcr_top1': False, 
        'a_hci': False, 
        'esci': False, 
        'scie': False, 
        'ssci': False, 
    })
    if i['src']['journal'].lower() in datasets['jcr'][:130]:
        i['src']['jcr_top1'] = True
        i['src']['jcr_q1'] = True
    if i['src']['journal'].lower() in datasets['jcr']:
        i['src']['jcr_q1'] = True
    
    if i['src']['journal'].lower() in datasets['a_hci']:
        i['src']['a_hci'] = True
    if i['src']['journal'].lower() in datasets['esci']:
        i['src']['esci'] = True
    if i['src']['journal'].lower() in datasets['scie']:
        i['src']['scie'] = True
    if i['src']['journal'].lower() in datasets['ssci']:
        i['src']['ssci'] = True
    counter += 1
    # print(counter, i['year'])
    # print(i['auts'])
    # print('---------------------------')

# printing out some preliminary results to see if everything runs OK
QS100 = []
QS300 = []
JCRQ1 = []
JCRTop1 = []
errors = []
warnings = []
for i in papers:
    if any(i['auts_affils'][cnt]['qs100'] == True for cnt in i['auts_affils']):
        QS100.append(i)
    if any(i['auts_affils'][cnt]['qs300'] == True for cnt in i['auts_affils']):
        QS300.append(i)

    if i['src']['jcr_q1'] == True:
        JCRQ1.append(i)
    if i['src']['jcr_top1'] == True:
        JCRTop1.append(i)
    
    if any(i['errors'][cnt]['value'] == True and i['errors'][cnt]['type'] == 'Error' for cnt in i['errors']):
        errors.append(i)
    if any(i['errors'][cnt]['value'] == True and i['errors'][cnt]['type'] == 'Warning' for cnt in i['errors']):
        warnings.append(i)

print('--------------------------------------------------')
print('QS100: ', len(QS100), '*** %: ', round(100 * len(QS100)/len(papers), 1), '*** Total: ', len(papers))
print('QS300: ', len(QS300), '*** %: ', round(100 * len(QS300)/len(papers), 1), '*** Total: ', len(papers))
print(f'Errors: {len(errors)} *** Warnings: {len(warnings)}')
# papers[105]

if type(db) == sqlite3.Connection:
    db.close()