# modules

import csv
from collections import OrderedDict
import sqlite3
import io
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# definitions, datasets

def in_list(query, items_list, any_all, idx = False):
    if idx and any_all == 'all':
        return
    elif idx and any_all == 'any':
        for cnt, item in enumerate(items_list):
            if query in item:
                return [True, cnt]
        return [False, -1]
    elif not idx and any_all == 'any':
        return any(query in item for item in items_list)
    elif not idx and any_all == 'all':
        return all(query in item for item in items_list)

def ordd_access(ord_dic, idx):
    key = list(ord_dic.keys())[idx]
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
        'Author Keywords': 'aut_key', 'Index Keywords': 'idx_key',
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
    'Electrical Engineering Department': 'EE',
    'Electrical Engineering School': 'EE',
    'Electrical Engineering Faculty': 'EE',
    'Aerospace Engineering Department': 'Aero',
    'Aerospace Engineering School': 'Aero',
    'Aerospace Engineering Faculty': 'Aero',
    'Computer Engineering Department': 'CE',
    'Computer Engineering School': 'CE',
    'Computer Engineering Faculty': 'CE',
    'Industrial Engineering Department': 'IE',
    'Industrial Engineering School': 'IE',
    'Industrial Engineering Faculty': 'IE',
    'Energy Engineering Department': 'Energy',
    'Energy Engineering School': 'Energy',
    'Energy Engineering Faculty': 'Energy',
    'Mechanical Engineering Department': 'Mech',
    'Mechanical Engineering School': 'Mech',
    'Mechanical Engineering Faculty': 'Mech',
    'Civil Engineering Department': 'Civil',
    'Civil Engineering School': 'Civil',
    'Civil Engineering Faculty': 'Civil',
    'Management and Economics Department': 'GSME',
    'Management and Economics School': 'GSME',
    'Management and Economics Faculty': 'GSME',
    'Graduate School of Management and Economics': 'GSME',
    'Materials Science and Engineering Department': 'MSE',
    'Materials Science and Engineering School': 'MSE',
    'Materials Science and Engineering Faculty': 'MSE',
    'Chemical and Petroleum Engineering Department': 'ChE',
    'Chemical and Petroleum Engineering School': 'ChE',
    'Chemical and Petroleum Engineering Faculty': 'ChE',
    'Chemistry Department': 'Chem',
    'Chemistry School': 'Chem',
    'Chemistry Faculty': 'Chem',
    'Physics Department': 'Phys',
    'Physics School': 'Phys',
    'Physics Faculty': 'Phys',
    'Mathematical Sciences Department': 'Math',
    'Mathematical Sciences School': 'Math',
    'Mathematical Sciences Faculty': 'Math',
    'Nanoscience and Nanotechnology Department': 'Nano',
    'Nanoscience and Nanotechnology School': 'Nano',
    'Nanoscience and Nanotechnology Faculty': 'Nano',
    'Nanoscience and Nanotechnology Institute': 'Nano',
    'Nanoscience and Nanotechnology institution': 'Nano',
    'Biochemical and Bioenvironmental Research Centre': 'Bio',
    'Philosophy of Science': 'PhilSci',
    'Languages and Linguistics Center': 'Lang',
    'Sharif Upstream Petroleum Research Institute (SUPRI)': 'Supri',
    'Sharif Upstream Petroleum Research Institute': 'Supri',
    'Design, Robotics, and Automation Center of Excellence (CEDRA)': 'CEDRA',
    'Design, Robotics, and Automation Center of Excellence': 'CEDRA',
    'Power System Management & Control Center of Excellence (CEPSMC)': 'CEPSMC',
    'Power System Management & Control Center of Excellence': 'CEPSMC',
    'Hydrodynamics & Dynamic of Marine Vehicles Center of Excellence (CEHDMV)': 'CEHDMV',
    'Hydrodynamics & Dynamic of Marine Vehicles Center of Excellence': 'CEHDMV',
    'Energy Conversion Center of Excellence (CEEC)': 'CEEC',
    'Energy Conversion Center of Excellence': 'CEEC',
    'Complex Systems and Condensed Matter Center of Excellence (CSCM)': 'CSCM',
    'Complex Systems and Condensed Matter Center of Excellence': 'CSCM',
}

dept_strings = [
    'department', 'depatment', 'school', 'faculty', 'nanotechnology institut',
    'institute for nano', 'institution for nano', 'center'
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
                        'first': row['First En'],
                        'last': row['Last En'],
                        'init': row['Initial En'],
                        'i_last': row['Initial En'] + ' ' + row['Last En'],
                        'depts': row['Dept'],
                        'scopus': [],
                    }
        else:
            datasets[db_name.lower()] = []
            with open(os.path.join(dataset_directory, file), encoding='UTF-16') as import_file:
                reader = csv.DictReader(import_file, dialect='excel-tab')
                for row in reader:
                    datasets[db_name.lower()].append(row[db_name].lower())

def splitter(
    string: str, split_char: str, out_type: str = 'ordd',
    strip: bool = True, vacuum = ''):

    if vacuum == '':
        vacuum = lambda item: item
    ls = string.split(split_char)
    if out_type == 'ordd':
        output = OrderedDict(
            (cnt, item.strip()) for cnt, item in enumerate(ls) if vacuum(item)
        )
    elif out_type == 'list':
        output = [item.strip() for item in ls if vacuum(item)]
    return output

def aut_country (
    raw_affil: list, country_data: dict,
    start_idx: int = 2, end_idx: int = None,
    home = 'IR', home_aliases = ['tehran', 'sharif']):
    
    countries = []
    duo_affil = False
    foreigner = False
    foreign = False
    affils = []

    position = start_idx
    for cnt, elem in enumerate(raw_affil[start_idx:end_idx]):
        if in_list(elem, country_data.keys(), 'any'):
            country_idx = in_list(elem, country_data.keys(), 'any', True)[1]
            country_idx = list(country_data.keys())[country_idx]
            countries.append(country_data[country_idx]['id'])
            
            affils.append(raw_affil[position:start_idx + cnt + 1])
            position = start_idx + cnt + 1

    if len(countries) > 1:
        duo_affil = True

    if not set(countries) & {home}:
        foreigner = True
        foreign = True
    elif set(countries) - {home}:
        foreign = True

    if not countries:
        for alias in home_aliases:
            if in_list(alias, raw_affil[start_idx:end_idx], 'any'):
                countries.append(home)
                break
    if not countries:
        countries.append('NOT FOUND')
    
    return [countries, duo_affil, foreigner, foreign, affils]

def db_handler(db_name, db_query_aut: str = '', year1 = '', year2 = 2018, close: bool = False):
    db = '' or sqlite3.connect(db_name)
    if close:
        if type(db) == sqlite3.Connection:
            db.close()
            return
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
                    Year >= cast(? as numeric) AND 
                    Year <= cast(? as numeric) AND 
                    Authors LIKE ?''', 
                (year1, year2, '%' + db_query_aut + '%',)
            )
        return cursor.fetchall()

def aut_dept(
    affils: list, dept_strings: list, sharif_depts: dict,
    cutoff: int, keyword: str = 'sharif'):

    # if 'sharif' in any affiliation, aut is Sharifi
    # we can also check to see whether aut's other affils are sharif or not
    sharif = False
    depts = []
    
    keyword = keyword.lower()
    for cnt, affil in enumerate(affils):
        depts.append({'sharif': False, 'dept': ''})
        if in_list(keyword, affil, 'any'):
            sharif = True
            depts[cnt]['sharif'] = True
            for elem in affil:
                if any(item in elem.lower() for item in dept_strings):
                    match = process.extractOne(
                        elem.strip(),
                        list(sharif_depts.keys()),
                        score_cutoff=cutoff
                    )
                    if match:
                        depts[cnt]['dept'] = sharif_depts[match[0]]
                    else:
                        depts[cnt]['dept'] = 'NOT MATCHED'
                    break
            if not depts[cnt]['dept']:
                depts[cnt]['dept'] = 'NOT FOUND'
        else:
            depts[cnt]['dept'] = 'NOT SHARIF'
    return [sharif, depts]

def aut_match(query: str, auts_dict: dict, key: str, cutoff: int):
    auts_list = [auts_dict[k][key] for k in auts_dict]
    match = process.extractOne(query, auts_list, score_cutoff=cutoff)
    if match:
        return [k for k in auts_dict if auts_dict[k][key] == match[0]][0]
    else:
        return 'NOT MATCHED'

def analyze_auts(db_query_aut, year1, year2, db_name, datasets, cutoff = 80):

    faculties = OrderedDict()
    for faculty in datasets['faculties'].keys():
        faculties[faculty] = []
    
    papers = db_handler(db_name, db_query_aut, year1, year2)
    for counter, i in enumerate(papers):

        i['affils'] = splitter(i['affils'], ';')
        i['auts_id'] = splitter(i['auts_id'], ';', out_type='list')
        i['auts'] = splitter(
            i['auts'], ',', vacuum=lambda item: len(item.strip()) > 3)
        auts_affils = splitter(i['auts_affils'], ';', out_type='list')
        
        if len(i['auts']) > 30:
            continue
        if len(i['auts']) != len(i['auts_id']):
            continue
        if len(auts_affils) != len(i['auts_id']):
            continue
        
        temp = OrderedDict()
        for cnt, aut in enumerate(auts_affils):
            temp[cnt] = {
                'raw_affil': aut, 'init': '', 'last': '', 'affils': [],
                'sharif': False, 'faculty': False, 'sharif_id': [],
                'depts': [], 'scopus_id': i['auts_id'][cnt],
                'duo_affil': False, 'countries': [],
                'foreign': False, 'foreigner': False,
            }
            
            aut_split = splitter(aut.lower(), ',', out_type='list')
            [temp[cnt]['last'], temp[cnt]['init']] = aut_split[0:2]

            [
                temp[cnt]['countries'],
                temp[cnt]['duo_affil'],
                temp[cnt]['foreigner'],
                temp[cnt]['foreign'],
                temp[cnt]['affils'],
            ] = aut_country (aut_split, datasets['countries'])
            
            if not temp[cnt]['foreigner']:
                [
                    temp[cnt]['sharif'],
                    temp[cnt]['depts'],
                ] = aut_dept(
                    temp[cnt]['affils'], dept_strings,
                    sharif_depts, cutoff, 'sharif'
                )
            if temp[cnt]['sharif']:
                i_last = temp[cnt]['init'] + ' ' + temp[cnt]['last']
                for dept in temp[cnt]['depts']:
                    if not 'NOT' in dept['dept']:
                        auts_dict = {k: v for k, v in datasets['faculties'].items() 
                            if dept['dept'] in v['depts']}
                        match = aut_match(i_last, auts_dict, 'i_last', 90)
                        if match != 'NOT MATCHED':
                            temp[cnt]['sharif_id'].append(match)
                if len(set(temp[cnt]['sharif_id'])) == 1:
                    temp[cnt]['sharif_id'] = temp[cnt]['sharif_id'][0]
                    temp[cnt]['faculty'] = True
                    print('MATCHED!')
                    print(i['doi'])
                    print(f"{i_last}******{temp[cnt]['sharif_id']}")
                    print('---------------')
                elif len(set(temp[cnt]['sharif_id'])) > 1:
                    print('MULTI')
                    print(i['doi'])
                    print(f"{i_last}******{temp[cnt]['sharif_id']}")
                    print('===============')
                else:
                    print("Couldn't Match or NOT FACULTY")
                    print(i['doi'])
                    print(i_last)
                    print('***************')
        i['auts_affils'] = temp

    db_handler(db_name, close=True)
    
    # with io.open('test.txt', 'w', encoding = "UTF-16") as tsvfile:
    #     tsvfile.write('sharif_id\tids')
    #     for i in faculties:
    #             exp_text = i + '\t' + ', '.join(faculties[i]) + '\n'
    #             tsvfile.write(exp_text)