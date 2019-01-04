# modules

import csv
from collections import OrderedDict
# from collections import Counter
import sqlite3
import io
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
# definitions, datasets

def in_list(query, items_list, any_all, index = False):
    if index and any_all == 'all':
        return
    elif index and any_all == 'any':
        for cnt, item in enumerate(items_list):
            if query in item:
                return [True, cnt]
        return [False, -1]
    elif not index and any_all == 'any':
        return any(query in item for item in items_list)
    elif not index and any_all == 'all':
        return all(query in item for item in items_list)

def ordd_access(ord_dic, ind):
    key = list(ord_dic.keys())[ind]
    return {key: ord_dic[key]}

def faculty_data(dept, faculties, author = ''):
    export = []
    for faculty in faculties:
        if dept in faculty['Dept']:
            export.append(faculty['Last English'].lower())
    if author == '':
        return export
    else:
        return [in_list(author.lower(), export, 'any'), ]

def dict_factory(cursor, row):
    key_map = {
        'Authors': 'auts', 'Author(s) ID': 'auts_id', 'Title': 'title',
        'Year': 'year', 'Source title': 'src', 'Volume': 'vol',
        'Issue': 'issue', 'Art. No.': 'art_no', 'Page start': 'pg_start',
        'Page end': 'pg_end', 'Page count': 'pg_count', 'Cited by': 'cites',
        'DOI': 'doi', 'Link': 'link', 'Affiliations': 'affils',
        'Authors with affiliations': 'auts_affils', 'Abstract': 'abs',
        'Author Keywords': 'aut_key', 'Index Keywords': 'ind_key',
        'Molecular Sequence Numbers': 'molecular_sequence_numbers',
        'Chemicals/CAS': 'cas', 'Tradenames': 'tradenames',
        'Manufacturers': 'manufacturers', 'Funding Details': 'fund',
        'References': 'refs', 'Correspondence Address': 'address',
        'Editors': 'editors', 'Sponsors': 'sponsors', 'Publisher': 'publisher',
        'Conference name': 'conf_name', 'Conference date': 'conf_date',
        'Conference location': 'conf_loc', 'Conference code': 'conf_code',
        'ISSN': 'issn', 'ISBN': 'isbn', 'CODEN': 'coden', 'PubMed ID': 'pubmed',
        'Language of Original Document': 'lang',
        'Abbreviated Source Title': 'abb_src', 'Document Type': 'doc_type',
        'Publication Stage': 'pub_stage', 'Access Type': 'access_type',
        'Source': 'source', 'EID': 'eid',
    }
    dic = OrderedDict()
    if key_map:
        for idx, col in enumerate(cursor.description):
            dic[key_map[col[0]]] = row[idx]
    else:
        for idx, col in enumerate(cursor.description):
            dic[col[0]] = row[idx]
    return dic

sharif_depts = {
    'Department of Electrical Engineering': 'EE',
    'Electrical Engineering Department': 'EE', 'Electrical Engineering': 'EE',
    'Department of Aerospace Engineering': 'Aero',
    'Aerospace Engineering Department': 'Aero', 'Aerospace Engineering': 'Aero',
    'Department of Computer Engineering': 'CE',
    'Computer Engineering Department': 'CE', 'Computer Engineering': 'CE',
    'Department of Industrial Engineering': 'IE',
    'Industrial Engineering Department': 'IE', 'Industrial Engineering': 'IE',
    'Department of Energy Engineering': 'Energy',
    'Energy Engineering Department': 'Energy', 'Energy Engineering': 'Energy',
    'Department of Mechanical Engineering': 'Mech',
    'Mechanical Engineering Department': 'Mech',
    'Mechanical Engineering': 'Mech',
    'School of Mechanical Engineering': 'Mech',
    'Department of Civil Engineering': 'Civil',
    'Civil Engineering Department': 'Civil', 'Civil Engineering': 'Civil',
    'Graduate School of Management and Economics': 'GSME',
    'Graduate School of Management & Economics': 'GSME',
    'Management and Economics': 'GSME', 'Management & Economics': 'GSME',
    'Department of Materials Science and Engineering': 'MSE',
    'Department of Materials Science & Engineering': 'MSE',
    'Materials Science and Engineering Department': 'MSE',
    'Materials Science & Engineering Department': 'MSE',
    'Materials Science and Engineering': 'MSE',
    'Materials Science & Engineering': 'MSE',
    'Department of Chemical and Petroleum Engineering': 'ChE',
    'Department of Chemical & Petroleum Engineering': 'ChE',
    'Chemical and Petroleum Engineering Department': 'ChE',
    'Chemical & Petroleum Engineering Department': 'ChE',
    'Chemical and Petroleum Engineering': 'ChE',
    'Chemical & Petroleum Engineering': 'ChE',
    'Department of Chemistry': 'Chem', 'Chemistry': 'Chem',
    'Chemistry Department': 'Chem',
    'Department of Physics': 'Phys', 'Physics': 'Phys',
    'Physics Department': 'Phys',
    'Department of Mathematical Sciences': 'Math', 'Mathematical': 'Math',
    'Institute for Nanoscience and Nanotechnology': 'Nano',
    'Institute for Nanoscience & Nanotechnology': 'Nano',
    'Nanoscience and Nanotechnology Institute': 'Nano',
    'Nanoscience & Nanotechnology Institute': 'Nano',
    'Institute for Nanoscience and Nanotechnology (INST)': 'Nano',
    'Institute for Nanoscience & Nanotechnology (INST)': 'Nano',
}

dept_strings = [
    'department', 'nanotechnology institut', 'school of mechanical engineering',
    'graduate school of management'
]

dataset_extention = ['txt', 'csv']
dataset_directory = 'datasets'

datasets = {}

for file in os.listdir(dataset_directory):
    if file.split('.')[1] in dataset_extention:
        db_name = file.split('.')[0]
        if db_name == 'Countries':
            datasets[db_name.lower()] = {}
            with open(os.path.join(dataset_directory, file), encoding='UTF-16') as import_file:
                reader = csv.DictReader(import_file, dialect='excel-tab')
                for row in reader:
                    datasets[db_name.lower()][row['Countries'].lower()] = {
                        'id': row['ID'],
                        'islamic': True if row['Islamic'] == 'True' else False,
                    }
        elif db_name == 'Faculties':
            datasets[db_name.lower()] = OrderedDict()
            with open(os.path.join(dataset_directory, file), encoding='UTF-8-sig') as import_file:
                reader = csv.DictReader(import_file)
                for row in reader:
                    datasets[db_name.lower()][row['ID']] = {
                        'first': row['First English'],
                        'last': row['Last English'],
                        'init': row['Initial English'],
                        'last_init': row['Last English'] + ' ' + row['Initial English'],
                        'last_i2': row['Last English'] + ' ' + row['Initial English'].replace('.', '').replace(' ', ''),
                        'dept': row['Dept'],
                        'scopus': [],
                    }
        else:
            datasets[db_name.lower()] = []
            with open(os.path.join(dataset_directory, file), encoding='UTF-16') as import_file:
                reader = csv.DictReader(import_file, dialect='excel-tab')
                for row in reader:
                    datasets[db_name.lower()].append(row[db_name].lower())


def analyze_auts(db_query_aut, year1, year2, db_name, datasets):

    faculties = OrderedDict()
    for faculty in datasets['faculties'].keys():
        faculties[faculty] = []
    db = '' or sqlite3.connect(db_name)

    if type(db) == sqlite3.Connection:
        db.row_factory = dict_factory
        cursor = db.cursor()
        if year1 == '':
            cursor.execute(
                '''SELECT * FROM papers WHERE Authors LIKE ?''', 
                ('%' + db_query_aut + '%',)
            )
        else:
            cursor.execute(
                '''SELECT * FROM papers WHERE 
                    Year >= cast(? as numeric) AND Year <= cast(? as numeric) AND 
                    Authors LIKE ?''', 
                (year1, year2, '%' + db_query_aut + '%',)
            )
        papers = cursor.fetchall()
    
    for counter, i in enumerate(papers):

        temp = OrderedDict()
        affils = i['affils'].split(';')
        for cnt, affil in enumerate(affils):
            temp[cnt] = affil.strip()
        i['affils'] = temp
        
        temp = OrderedDict()
        scopus_ids = list(filter(lambda id: id != '', i['auts_id'].split(';')))
        authors = i['auts'].split(',')
        authors = list(filter(lambda item: len(item.strip()) > 3, authors))
        if len(authors) > 30:
            continue
        for cnt, author in enumerate(authors):
            temp[cnt] = author.strip()
        i['auts'] = temp
        
        auts_affil = list(map(lambda elem: elem.strip(), i['auts_affils'].split(';')))
        if len(authors) != len(scopus_ids) or len(auts_affil) != len(scopus_ids):
            continue
        
        temp = OrderedDict()
        for cnt, aut in enumerate(auts_affil):
            temp[cnt] = {
                'name_address': aut.strip(),
                'sharif': False, 'faculty': False, 'sharif_id': '', 'dept': '',
                'scopus_id': scopus_ids[cnt], 'double_affil': False,
                'country': [],
            }
            qquery = aut.split(',')[0].strip() + ' ' + aut.split(',')[1].strip()
            qquery = qquery.lower()
            aut_split = aut.lower().split(',')
            for elem in aut_split:
                if in_list(elem.strip(), datasets['countries'].keys(), 'any'):
                    country_index = in_list(elem.strip(), datasets['countries'].keys(), 'any', True)[1]
                    country_index = list(datasets['countries'].keys())[country_index]
                    temp[cnt]['country'].append(datasets['countries'][country_index]['id'])

            if in_list('sharif', aut.lower().split(',')[2:], 'any'):
                temp[cnt]['sharif'] = True
                for elem in aut.split(','):
                    if any(item in elem.lower().strip() for item in dept_strings):
                        if len(temp[cnt]['country']) <= 1:
                            try:
                                temp[cnt]['dept'] = sharif_depts[elem.strip()]
                                break
                            except:
                                print(i['doi'])
                                print(elem.strip())
                                print()
                                print(aut)
                                print('----------------')
                                continue
                        else:
                            # print(f"dobule affils: {temp[cnt]['country']}")
                            # print(i['doi'])
                            # print('-/-/-/-/-/-/-/-/-/-/-/-/-/-/-')
                            if elem.strip() in sharif_depts.keys():
                                temp[cnt]['dept'] = sharif_depts[elem.strip()]
                                break
                            else:
                                continue
                    else:
                        temp[cnt]['dept'] = 'no_dept'
                if temp[cnt]['dept'] == '':
                    print(i['doi'])
                    print()
                    print(aut)
                    print('*****************')

            if in_list('sharif', aut.lower().split(',')[2:], 'any'):
                temp[cnt]['sharif'] = True
                [temp[cnt]['faculty'], temp[cnt]['sharif_id']] = in_list(
                    qquery,
                    [datasets['faculties'][faculty]['last_init'].lower() for faculty in datasets['faculties']],
                    'any',
                    True
                )
                if temp[cnt]['faculty']:
                    temp[cnt]['sharif_id'] = list(datasets['faculties'].keys())[temp[cnt]['sharif_id']]
                    faculties[temp[cnt]['sharif_id']].append(scopus_ids[cnt])
                    faculties[temp[cnt]['sharif_id']] = list(set(faculties[temp[cnt]['sharif_id']]))
                    temp[cnt]['dept'] = datasets['faculties'][temp[cnt]['sharif_id']]['dept']
                else:
                    temp[cnt]['sharif_id'] = ''
                    for elem in aut.split(','):
                        if 'department' in elem.lower() or 'institute' in elem.lower():
                            elem = elem.strip()
                            temp[cnt]['dept'] = elem

        i['auts_affils'] = temp

    if type(db) == sqlite3.Connection:
        db.close()
    
    with io.open('test.txt', 'w', encoding = "UTF-16") as tsvfile:
        tsvfile.write('sharif_id\tids')
        for i in faculties:
                exp_text = i + '\t' + ', '.join(faculties[i]) + '\n'
                tsvfile.write(exp_text)