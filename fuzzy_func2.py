# modules

import csv
from collections import OrderedDict
import sqlite3
import io
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# variables, functions, and datasets
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
    'Electronics Research Institute (ERI)': 'ERI',
    'Electronics Research Institute': 'ERI',
    'Institute of Water and Energy (IWE)': 'IWE',
    'Institute of Water and Energy': 'IWE',
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
            with open(
                os.path.join(dataset_directory, file), encoding='UTF-16'
            ) as import_file:

                reader = csv.DictReader(import_file, dialect='excel-tab')
                for row in reader:
                    datasets[db_name.lower()][row['Countries'].lower()] = {
                        'id': row['ID'],
                        'islamic': True if row['Islamic'] == 'True' else False,
                    }
        elif db_name == 'Faculties':
            datasets[db_name.lower()] = OrderedDict()
            with open(
                os.path.join(dataset_directory, file), encoding='UTF-8-sig'
            ) as import_file:

                reader = csv.DictReader(import_file)
                for row in reader:
                    datasets[db_name.lower()][row['ID']] = {
                        'first': row['First En'],
                        'last': row['Last En'],
                        'init': row['Initial En'],
                        'i_last': row['Initial En'] + ' ' + row['Last En'],
                        'depts': row['Dept'],
                    }
                    if row['Scopus']:
                        datasets[db_name.lower()][row['ID']]['scopus'] = set(
                            row['Scopus'].split(';')
                        )
                    else:
                        datasets[db_name.lower()][row['ID']]['scopus'] = set()
        # else:
        #     datasets[db_name.lower()] = []
        #     with open(
        #         os.path.join(dataset_directory, file), encoding='UTF-16'
        #     ) as import_file:

        #         reader = csv.DictReader(import_file, dialect='excel-tab')
        #         for row in reader:
        #             datasets[db_name.lower()].append(row[db_name].lower())

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

def aut_dept(
    affils: list, dept_strings: list, sharif_depts: dict,
    cutoff: int, keyword: str = 'sharif'):

    # if 'sharif' in any affiliation, aut is Sharifi
    # we can also check to see whether aut's other affils are sharif or not
    has_keyword = False
    depts = []
    
    keyword = keyword.lower()
    for cnt, affil in enumerate(affils):
        depts.append({'sharif': False, 'dept': ''})
        if in_list(keyword, affil, 'any'):
            has_keyword = True
            depts[cnt][keyword] = True
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
            depts[cnt]['dept'] = 'NOT ' + keyword.upper()
    return [has_keyword, depts]

def aut_match(query: str, auts_dict: dict, key: str, cutoff: int):
    auts_list = [auts_dict[k][key] for k in auts_dict]
    match = process.extractOne(query, auts_list, score_cutoff=cutoff)
    if match:
        return [k for k in auts_dict if auts_dict[k][key] == match[0]][0]
    else:
        return 'NOT MATCHED'

def db_handler(
    db_name, db_query_aut: str = '', year1 = '', year2 = 2018,
    close: bool = False):

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



def analyze_auts(
    db_query_aut, year1, year2, db_name, datasets,
    cutoff = 80, new_count = False, filtered_export = True, threshold = 5):
    
    if new_count:
        for i in datasets['faculties']:
            datasets['faculties'][i]['scopus'] = {}

    papers = db_handler(db_name, db_query_aut, year1, year2)
    for i in papers:

        # Extracting affiliations, Scopus author ids and author names
        i['affils'] = splitter(i['affils'], ';')
        i['auts_id'] = splitter(i['auts_id'], ';', out_type='list')
        i['auts'] = splitter(
            i['auts'], ',', vacuum=lambda item: len(item.strip()) > 3)
        auts_affils = splitter(i['auts_affils'], ';', out_type='list')
        
        # Ignoring papers with too many authors involved!
        if len(i['auts']) > 30:
            continue
        if len(i['auts']) != len(i['auts_id']):
            continue
        if len(auts_affils) != len(i['auts_id']):
            continue
        
        # Scopus as this format for each of the paper's authors:
        #
        # Last Name, Initials, Department, University, City, Country
        #
        # For each author, we create a template profile and then work our way
        # from outside (Country) to inside (Author's name) by matching strings:
        #
        # - raw_affil: Authors_with_Affiliations string
        # - init     : Author's initials
        # - last     : Author's last name (raw_affil doesn't contain first name)
        # - sharif   : True if any of an author's affiliations is Sharif
        # - faculty  : True if the author in datasets['faculties'] (only Sharif)
        # - sharif_id: Unique ID that Sharif gives its faculty members, used
        #              here to connect 'faculties' dataset with Scopus data
        # - depts    : A list of author's affiliated Sharif departments
        # - scopus_id: Author's ID in Scopus
        # - duo_affil: True if the author is has more that 1 affiliation
        # - affils   : A list of all of the author's affiliations
        # - countries: Each of the author's affils has a country
        # - foreign  : True if the author has at least 1 foreign affil
        # - foreigner: True if all of the author's affils are foreign
        temp = OrderedDict()
        for cnt, aut in enumerate(auts_affils):
            temp[cnt] = {
                'raw_affil': aut, 'init': '', 'last': '',
                'sharif': False, 'faculty': False, 'sharif_id': [], 'depts': [],
                'scopus_id': i['auts_id'][cnt],
                'duo_affil': False,  'affils': [], 'countries': [],
                'foreign': False, 'foreigner': False,
            }
            
            aut_split = splitter(aut.lower(), ',', out_type='list')
            [temp[cnt]['last'], temp[cnt]['init']] = aut_split[0:2]

            # Matching countries
            [
                temp[cnt]['countries'],
                temp[cnt]['duo_affil'],
                temp[cnt]['foreigner'],
                temp[cnt]['foreign'],
                temp[cnt]['affils'],
            ] = aut_country(aut_split, datasets['countries'])
            
            # Matching university & departments
            if not temp[cnt]['foreigner']:
                [
                    temp[cnt]['sharif'],
                    temp[cnt]['depts'],
                ] = aut_dept(
                    temp[cnt]['affils'], dept_strings,
                    sharif_depts, cutoff, 'sharif'
                )
            
            # Matching author's name with faculties in each Sharif department
            sharif_id = []
            if temp[cnt]['sharif']:
                i_last = temp[cnt]['init'] + ' ' + temp[cnt]['last']
                for dept in temp[cnt]['depts']:
                    if not 'NOT' in dept['dept']:
                        auts_dict = {
                            k: v for k, v in datasets['faculties'].items() 
                            if dept['dept'] in v['depts']
                        }
                        match = aut_match(i_last, auts_dict, 'i_last', 90)
                        if match != 'NOT MATCHED':
                            sharif_id.append(match)
                if len(set(sharif_id)) == 1: # Faculty matched correctly
                    sharif_id = sharif_id[0]
                    temp[cnt]['sharif_id'] = sharif_id
                    temp[cnt]['faculty'] = True
                    try:
                        datasets['faculties'][sharif_id]['scopus'][i['auts_id'][cnt]] += 1
                    except KeyError:
                        datasets['faculties'][sharif_id]['scopus'][i['auts_id'][cnt]] = 1
                elif len(set(sharif_id)) > 1: # Multiple matches for a faculty
                    temp[cnt]['sharif_id'] = 'MULTIPLE MATCHES'
                else: # Could not match for a faculty
                    temp[cnt]['sharif_id'] = 'NOT MATCHED'
        
        i['auts_affils'] = temp

    db_handler(db_name, close=True)
    
    # Exporting the results
    if filtered_export:
        with io.open('scopus_ids_filtered.txt', 'w', encoding='UTF-16') as tsvfile:
            tsvfile.write('ID\tScopus\n')
            for k, v in datasets['faculties'].items():
                if v['scopus']:
                    if (
                        len(v['scopus']) > 1 and
                        max(v['scopus'].values()) >= threshold
                    ):
                        ids = list(
                            filter(
                                lambda item: v['scopus'][item] >= threshold,
                                v['scopus']
                            )
                        )
                        print(ids)
                        print('-----')
                    else:
                        ids = [max(v['scopus'], key=lambda item: v['scopus'][item])]
                        print(ids)
                        print('*****')
                    exp_text = k + '\t' + ';'.join([str((item, v['scopus'][item])) for item in ids]) + '\n'
                    ids = []
                else:
                    exp_text = k + '\t' + '' + '\n'
                tsvfile.write(exp_text)
    else:
        with io.open('scopus_ids_all.txt', 'w', encoding = "UTF-16") as tsvfile:
            tsvfile.write('ID\tScopus\n')
            for k, v in datasets['faculties'].items():
                if v['scopus']:
                    ids = list(v['scopus'].keys())
                    exp_text = k + '\t' + ';'.join([str((item, v['scopus'][item])) for item in ids]) + '\n'
                    ids = []
                else:
                    exp_text = k + '\t' + '' + '\n'
                tsvfile.write(exp_text)