# modules

import csv
from collections import OrderedDict
import sqlite3
import io
import os
from fuzzywuzzy import process
# ------------------------------------------------------------------------------
# variables, functions, and datasets

# This dictionary is used to match and unify the name of the department/research
# center/institute of authors who are affiliated with Sharif. For example,
# regardless of how an author from electrical engineering has submitted his/her
# department name (like school of electrical engineering, or electrical
# engineering faculty), it will be changed to 'EE'
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

# This variable is used to detect the part of the affiliation string which
# contains the name of the department of the author
dept_alias = [
    'department', 'depatment', 'school', 'faculty', 'nanotechnology institut',
    'institute for nano', 'institution for nano', 'center'
]

# There are many datasets used by the functions defined below. These include:
#
# A_HCI    : Contains a list of journal names that comprise the A&HCI index
# ESCI     : Contains a list of journal names that comprise the ESCI index
# SCIE     : Contains a list of journal names that comprise the SCIE index
# SSCI     : Contains a list of journal names that comprise the SSCI index
# JCR      : Contains a list of journal names that comprise the JCR list
# QS**     : Lists of top 100/top 101-300 universities according to QS
# Faculties: A complete list of all Sharif faculty members, which include their
#            name in Farsi & English, contact info, email, and much more
# Countries: A complete list of all countries in the world. For each country, it
#            is specified whether the country is Islamic or not. Additional info
#            can also be added, like the continent of each country ??

# The code below tries to import these datasets. I still haven't find a way to
# create a neat, short function that does the job
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
                        'co_auts': {}, 'cnt': 0,
                    }
                    if row['Scopus']:
                        datasets[db_name.lower()][row['ID']]['scopus'] = list(
                            map(lambda item: eval(item), row['Scopus'].split(';'))
                        )
                    else:
                        datasets[db_name.lower()][row['ID']]['scopus'] = []

def dict_factory(cursor, row):
    
    # This function is used to import data from SQL database as an OrderedDict
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
        'References': 'refs', 'Correspondence Address': 'corr_address',
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

def db_handler(
    db_name: str, db_query_aut: str = '', year1: int = 0, year2: int = 2018,
    add_keys: list = [], close: bool = False, factory = dict_factory):
    
    # This function can either import data from SQL database or close the
    # connection made to it. Arguments:
    #
    # db_name     : Name of the '.db' file to import the data from or to close
    # db_query_aut: Name of author to search for, can be left empty to find all
    # year1       : Specifies the year that papers are published in or after
    # year2       : Specifies the year that papers are published in or before
    # add_keys    : The ability of adding arbitrary columns to the imported data
    # close       : If true, the function will close the connection to database
    # factory     : Specifies the method of import of data
    db = sqlite3.connect(db_name)
    if close:
        db.close()
        return
    
    db.row_factory = factory
    cursor = db.cursor()
    if not year1: # Special case: import everything in the SQL database
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
    output = cursor.fetchall()
    if add_keys:
        for i in output:
            for tup in add_keys:
                i[tup[0]] = tup[1]
    return output

def in_list(query, str_list, any_all, idx = False):
    
    # On many occasions, the algorithm needs to check whether a string is part
    # of any/all strings in a list and to return the position. Arguments:
    #
    # query   : The string that we want to find in other strings
    # str_list: A list of strings that we search for the query in
    # any_all : Can either by 'any' or 'all' which tells how to search for query
    # idx     : If true, makes the function to return the position of query
    #           inside the str_list. Returns -1 if not found.
    if idx and any_all == 'all':
        return
    elif idx and any_all == 'any':
        for cnt, item in enumerate(str_list):
            if query in item:
                return [True, cnt]
        return [False, -1]
    elif not idx and any_all == 'any':
        return any(query in item for item in str_list)
    elif not idx and any_all == 'all':
        return all(query in item for item in str_list)

def splitter(
    string: str, split_char: str, out_type: str = 'ordd',
    strip: bool = True, vacuum = ''):
    
    # The raw data the database are long strings joined by characters like ';'
    # To analyze the data, we need to separate and clean different chunks of
    # these strings, which is the use case of this function. Arguments:
    #
    # string    : Raw string to be divided and cleaned
    # split_char: The charater by which we split the raw string
    # out_type  : Tells the function to return an OrderedDict or a list
    # strip     : If true, trims the white spaces from around each chunk
    # vacuum    : A function that performs additional process on each chunk
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

def paper_check(paper: OrderedDict, auts_count: int = 30):
    
    # Extract information such as author name, id, and affiliation from each
    # paper and then performs common checks to see if the paper is ok for
    # inspection or not. Arguments:
    # 
    # paper     : An OrderedDict containing all the information for a paper
    # auts_count: Specifies the maximum number of authors per paper. If  more,
    #             ignore the paper
    
    # Extracting affiliations, Scopus author ids and author names
    # Usually author names are longer than 3 characters (last + ' ' + initial)
    auts = splitter(
        paper['auts'], ',', vacuum=lambda item: len(item.strip()) > 3)
    auts_id = splitter(paper['auts_id'], ';', out_type='list')
    auts_affils = splitter(paper['auts_affils'], ';', out_type='list')
    
    # Ignoring papers with too many authors involved!
    if (
        len(auts) > auts_count or 
        len(auts) != len(auts_id) or 
        len(auts_affils) != len(auts_id)
    ):
        return []
    return [auts, auts_id, auts_affils]

def aut_country (
    raw_affil: list, country_data: dict,
    start_idx: int = 2, end_idx: int = None,
    home = 'IR', home_aliases = ['tehran', 'sharif'],
    ignore = ['department', 'university', 'institut', 'center', 'school']):
    
    # This function receives a string of affiliation and from it, determines:
    #
    # - The author's country (using 'Countries' dataset)
    # - Whether the author has multiple affiliations (by checking if there are
    #   more than 1 country names in the affiliation)
    # - If the author is a 'foreigner' (meaning he/she isn't affiliation with
    #   the 'home' country)
    # - If the author has any foreign affiliation
    # 
    # The function also returns a list of affiliations if there are more than 1.
    # Arguments:
    #
    # raw_affil   : A string containing the raw affiliation of the author
    # country_data: The 'Countries' dataset
    # start_idx   : Usually, the first 2 parts of the affiliation string is the
    #               author's name, so we ignore it and check from the 3rd place
    # end_idx     : Not used ??
    # home        : Used to determine 'foreign' countries. If we consider Sharif
    #               University, 'home' will be 'IR' and so an author with other
    #               countries in his/her string will have foreign affiliation
    # home_aliases: A list of popular names that indicate the country of the
    #               author, if the country name is not in the string.
    # ignore      : A list of popular names for department/university/etc that
    #               makes the function ignore the chunk of text containing it
    #               to find better results
    countries = []
    multi_affil = False
    foreigner = False
    foreign = False
    affils = []

    position = start_idx
    for cnt, elem in enumerate(raw_affil[start_idx:end_idx]):
        if (
            in_list(elem, country_data.keys(), 'any') and
            all(ign not in elem for ign in ignore) and
            (# country names usually have more than 3 characters except these:
                elem.lower() in ['usa', 'uk', 'uae'] or
                len(elem) > 3
            )
        ):  # we don't use fuzzy match for country names for improved accuracy
            country_idx = in_list(elem, country_data.keys(), 'any', True)[1]
            country_idx = list(country_data.keys())[country_idx]
            countries.append(country_data[country_idx]['id'])
            
            # when a country name is found, continue with the rest of the string
            affils.append(raw_affil[position:start_idx + cnt + 1])
            position = start_idx + cnt + 1

    if len(countries) > 1:
        multi_affil = True
    
    # If 'home' not found in countries, the author is a foreigner
    if (not set(countries) & {home}) and (set(countries)):
        foreigner = True
        foreign = True
    # Author might not be a foreigner, but have foreign affiliation regardless
    elif set(countries) - {home}:
        foreign = True
    
    # If no country found, use 'home_aliases' to detect if author is domestic
    if not countries:
        for alias in home_aliases:
            if in_list(alias, raw_affil[start_idx:end_idx], 'any'):
                countries.append(home)
                break
    if not countries:
        countries.append('NOT FOUND')
    
    return [countries, multi_affil, foreigner, foreign, affils]

def aut_dept(
    affils: list, dept_alias: list, sharif_depts: dict,
    cutoff: int, keyword: str = 'sharif'):

    # After determining the author's country, it's time to detect if he/she is
    # from the institution that we try to analyze or not (in this case 'Sharif')
    # If author is from Sharif, we the proceed to find out which department.
    # Note that an author with multiple affiliations could have some but not all
    # of his/her affiliations with Sharif. Argument:
    #
    # affils      : A list of affiliations for each author, from aut_country()
    # dept_alias  : A list of common names for department/research center/etc.
    # sharif_depts: A dictionary that maps common names for Sharif department to
    #               Their abbreviations
    # cutoff      : An integer which tells the fuzzywuzzy package how good a
    #               match we are looking for (higher means better, 100 maximum)
    # keyword     : A word that determines if the author is from our institute

    has_keyword = False
    depts = []
    
    keyword = keyword.lower()
    for cnt, affil in enumerate(affils):
        depts.append({keyword: False, 'dept': ''})
        if in_list(keyword, affil, 'any'):
            has_keyword = True
            depts[cnt][keyword] = True
            for elem in affil: # now we search for the department
                if any(item in elem.lower() for item in dept_alias):
                    # department found, now we match it with sharif_depts
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

def aut_match(query: str, dept_profs: dict, key: str, cutoff: int):
    
    # After determining the department authors affiliated with Sharif, we then
    # proceed to check whether he/she is a faculty member. For that, we have a
    # list of Sharif faculties and we extract those that are in the same
    # department with the current author to improve the results. Arguments:
    # 
    # query     : Name of the author in the format:
    #             initial + last name (J. Smith)
    # dept_profs: A subset of all faculty members that have the same department
    #             as the author
    # key       : Name of the key in the dept_profs that have the names of
    #             faculties in a format like query (i + last)
    # cutoff    : An integer which tells the fuzzywuzzy package how good a
    #             match we are looking for (higher means better, 100 maximum)
    auts_list = [dept_profs[k][key] for k in dept_profs]
    match = process.extractOne(query, auts_list, score_cutoff=cutoff)
    if match:
        return [k for k in dept_profs if dept_profs[k][key] == match[0]][0]
    else:
        return 'NOT MATCHED'

def corr_aut(corr_address: str, auts_affils: list):
    
    # This function is used to extract and clean ?? the email address of the
    # corresponding author of each paper (if there are any). If found, we match
    # it to one of the authors in the paper, if not retrun -1
    if 'email: ' in corr_address.lower() and ';' in corr_address:
        name = corr_address.split(';')[0]
        email = corr_address.lower().split('email: ')[1].strip()
        if (
            email.count('@') == 1 and 
            email.count(' ') == 0 and 
            email.split('@')[1].count('.') >= 1
        ):
            idx = in_list(name, auts_affils, 'any', True)[1]
            return [email, idx]
        else:
            return ['BAD EMAIL', -1]
    else:
        return ['NOT FOUND', -1]

def exp_emails(
    db_name, cutoff: int = 0, exp_name: str = 'corr_emails.txt'):
    
    # This function loops through all papers and extracts the email addresses
    # using corr_aut(). It can then save the results to a file or return a
    # dictionary. Arguments:
    #
    # db_name : The name of database file, or the 'already imported database'
    # cutoff  : Sometimes author's change their institute and so old emails
    #           might not be valid anymore. This arguments tells the function
    #           to ignore emails from papers that are published before a
    #           certain year. If 0, extracts all emails.
    # exo_name: Name of the export file. If empty, function will return a dict
    if type(db_name) == str:
        papers = db_handler(db_name, '', '', 2018)
        db_handler(db_name, close=True)
    else:
        papers = db_name
    
    authors = {}
    for i in papers:
        paper_info = paper_check(i)
        if paper_info:
            [auts, auts_id, auts_affils] = paper_info
        else:
            continue
        year = int(i['year'])
        if year < cutoff:
            continue
        
        [corr_email, idx] = corr_aut(i['corr_address'], auts_affils)
        if idx > -1:
            aut_id = auts_id[idx]
            if aut_id not in authors.keys():
                authors[aut_id] = {
                    'name': set(), 'year': 0, 'affil': '', 'email': '',
                }
            
            authors[aut_id]['name'].add(auts[idx])
            if year > authors[aut_id]['year']:
                authors[aut_id]['year'] = year
                authors[aut_id]['affil'] = auts_affils[idx]
                authors[aut_id]['email'] = corr_email
    if not exp_name:
        return authors
    with io.open(exp_name, 'w', encoding = "UTF-16") as tsvfile:
        tsvfile.write('Scopus ID\tName\tYear\tAffil\tEmail\n')
        for k, v in authors.items():
            exp_text = k + '\t'
            exp_text += ';'.join(v['name']) + '\t' + str(v['year']) + '\t'
            exp_text += v['affil'] + '\t' + v['email'] + '\n'
            tsvfile.write(exp_text)

def analyze_auts(
    db_query_aut: str, year1: int, year2: int, db_name: str, datasets,
    dept_alias, sharif_depts, cutoff: int = 80, new_count: bool = False,
    exp_name: str = 'scopus_ids.txt',
    filtered_export: bool = True, threshold: int = 5):
    
    # ??
    if new_count:
        for i in datasets['faculties']:
            datasets['faculties'][i]['scopus'] = {}

    papers = db_handler(db_name, db_query_aut, year1, year2)
    db_handler(db_name, close=True)
    for i in papers:

        paper_info = paper_check(i)
        if paper_info:
            [auts_id, auts_affils] = paper_info[1:]
        else:
            continue
        
        [corr_email, idx] = corr_aut(i['corr_address'], auts_affils)

        # Scopus as this format for each of the paper's authors:
        #
        # Last Name, Initials, Department, University, City, Country
        #
        # For each author, we create a template profile and then work our way
        # from outside (Country) to inside (Author's name) by matching strings:
        #
        # - raw_affil  : Authors_with_Affiliations string
        # - init       : Author's initials
        # - last       : Author's last name (Scopus doesn't contain first name)
        # - sharif     : True if any of an author's affiliations is Sharif
        # - faculty    : True if the author in 'faculties' dataset (only Sharif)
        # - sharif_id  : Unique ID that Sharif gives its faculty members, used
        #                here to connect 'faculties' dataset with Scopus data
        # - depts      : A list of author's affiliated Sharif departments
        # - scopus_id  : Author's ID in Scopus
        # - multi_affil: True if the author is has more that 1 affiliation
        # - affils     : A list of all of the author's affiliations
        # - countries  : Each of the author's affils has a country
        # - foreign    : True if the author has at least 1 foreign affil
        # - foreigner  : True if all of the author's affils are foreign
        temp = OrderedDict()
        for cnt, aut in enumerate(auts_affils):
            temp[cnt] = {
                'raw_affil': aut, 'init': '', 'last': '',
                'sharif': False, 'faculty': False, 'sharif_id': [], 'depts': [],
                'scopus_id': auts_id[cnt],
                'multi_affil': False,  'affils': [], 'countries': [],
                'foreign': False, 'foreigner': False,
                'corr_aut': False, 'corr_email': '',
            }
            if idx == cnt:
                temp[cnt]['corr_aut'] = True
                temp[cnt]['corr_email'] = corr_email

            aut_split = splitter(aut.lower(), ',', out_type='list')
            [temp[cnt]['last'], temp[cnt]['init']] = aut_split[0:2]

            # Matching countries
            [
                temp[cnt]['countries'],
                temp[cnt]['multi_affil'],
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
                    temp[cnt]['affils'], dept_alias,
                    sharif_depts, cutoff, 'sharif'
                )
            
            # Matching author's name with faculties in each Sharif department
            sharif_id = []
            if temp[cnt]['sharif']:
                i_last = temp[cnt]['init'] + ' ' + temp[cnt]['last']
                for dept in temp[cnt]['depts']:
                    if not 'NOT' in dept['dept']:
                        dept_profs = {
                            k: v for k, v in datasets['faculties'].items() 
                            if dept['dept'] in v['depts']
                        }
                        match = aut_match(i_last, dept_profs, 'i_last', 90)
                        if match != 'NOT MATCHED':
                            sharif_id.append(match)
                if len(set(sharif_id)) == 1: # Faculty matched correctly
                    sharif_id = sharif_id[0]
                    temp[cnt]['sharif_id'] = sharif_id
                    temp[cnt]['faculty'] = True
                    try:
                        datasets['faculties'][sharif_id]['scopus'][auts_id[cnt]] += 1
                    except KeyError:
                        datasets['faculties'][sharif_id]['scopus'][auts_id[cnt]] = 1
                elif len(set(sharif_id)) > 1: # Multiple matches for a faculty
                    temp[cnt]['sharif_id'] = 'MULTIPLE MATCHES'
                else: # Could not match for a faculty
                    temp[cnt]['sharif_id'] = 'NOT MATCHED'
        i['auts_affils'] = temp
    
    # Exporting the results
    if filtered_export:
        with io.open(
            exp_name, 'w', encoding='UTF-16') as tsvfile:
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
                    else:
                        ids = [max(v['scopus'], key=lambda item: v['scopus'][item])]
                    exp_text = k + '\t' + ';'.join(
                        [str((item, v['scopus'][item])) for item in ids]) + '\n'
                    ids = []
                else:
                    exp_text = k + '\t' + '' + '\n'
                tsvfile.write(exp_text)
    else:
        with io.open(exp_name, 'w', encoding = "UTF-16") as tsvfile:
            tsvfile.write('ID\tScopus\n')
            for k, v in datasets['faculties'].items():
                if v['scopus']:
                    ids = list(v['scopus'].keys())
                    exp_text = k + '\t' + ';'.join(
                        [str((item, v['scopus'][item])) for item in ids]) + '\n'
                    ids = []
                else:
                    exp_text = k + '\t' + '' + '\n'
                tsvfile.write(exp_text)

def analyze_co_auts(
    db_query_aut: str, year1: int, year2: int, db_name: str, datasets,
    dept_alias, sharif_depts, cutoff: int = 80, exp_name: str = 'co_aut.txt'):
    
    # ??
    papers = db_handler(
        db_name, db_query_aut, year1, year2, add_keys=[('skip', False)])
    db_handler(db_name, close=True)

    emails = exp_emails(papers, cutoff=0, exp_name='')

    for p, prof in datasets['faculties'].items():
        if not prof['scopus']:
            continue
        for i in papers:
            if i['skip']:
                continue
            if type(i['auts_id']) == str:
                paper_info = paper_check(i)
                if paper_info:
                    [i['auts_id'], i['auts_affils']] = paper_info[1:]
                else:
                    continue

                temp = OrderedDict()
                for cnt, aut in enumerate(i['auts_affils']):
                    temp[cnt] = {
                        'raw_affil': aut, 'init': '', 'last': '',
                        'sharif': False, 'depts': [],
                        'scopus_id': i['auts_id'][cnt],
                        'multi_affil': False, 'affils': [], 'countries': [],
                        'foreign': False, 'foreigner': False,
                    }
                    aut_split = splitter(aut.lower(), ',', out_type='list')
                    [temp[cnt]['last'], temp[cnt]['init']] = aut_split[0:2]
                    [
                        temp[cnt]['countries'], temp[cnt]['multi_affil'],
                        temp[cnt]['foreigner'], temp[cnt]['foreign'],
                        temp[cnt]['affils'],
                    ] = aut_country(aut_split, datasets['countries'])
                    if not temp[cnt]['foreigner']:
                        [
                            temp[cnt]['sharif'], temp[cnt]['depts'],
                        ] = aut_dept(
                            temp[cnt]['affils'], dept_alias,
                            sharif_depts, cutoff, 'sharif'
                        )
                i['auts_affils'] = temp
            if any(scop[0] in i['auts_id'] for scop in prof['scopus']):
                co_auts = [
                    item for item in i['auts_id'] if item not in prof['scopus'][0]
                ]
                for aut in co_auts:
                    idx = i['auts_id'].index(aut)
                    if aut not in prof['co_auts'].keys():
                        prof['co_auts'][aut] = {
                            'cnt': 0,
                            'name'       : (
                                i['auts_affils'][idx]['init'] + ' ' +
                                i['auts_affils'][idx]['last']
                            ),
                            'raw_affil'  : i['auts_affils'][idx]['raw_affil'],
                            'multi_affil': i['auts_affils'][idx]['multi_affil'],
                            'countries'  : i['auts_affils'][idx]['countries'],
                            'foreigner'  : i['auts_affils'][idx]['foreigner'],
                            'foreign'    : i['auts_affils'][idx]['foreign'],
                            'affils'     : i['auts_affils'][idx]['affils'],
                            'sharif'     : i['auts_affils'][idx]['sharif'],
                            'email_year' : '',
                            'email'      : '',
                            'papers'     : {},
                        }
                    if i['year'] not in prof['co_auts'][aut]['papers'].keys():
                        prof['co_auts'][aut]['papers'][i['year']] = {
                            'cnt': 0, 'doi': []
                        }
                    prof['cnt'] += 1
                    prof['co_auts'][aut]['cnt'] += 1
                    prof['co_auts'][aut]['papers'][i['year']]['cnt'] += 1
                    prof['co_auts'][aut]['papers'][i['year']]['doi'].append(
                        i['doi'])
                    if aut in emails.keys():
                        prof['co_auts'][aut]['email_year'] = emails[aut]['year']
                        prof['co_auts'][aut]['email'] = emails[aut]['email']

    with io.open(exp_name, 'w', encoding='UTF-16') as tsvfile:
        header = [
            'First', 'Last', 'Init', 'i_last', 'Depts',
            'co_auts_id', 'Total', 'Name', 'Raw Affil', 'Multi Affil',
            'Countries', 'Foreigner', 'Foreign Affil', 'Sharif',
            'email_year', 'Email', 'Years', 'DOIs',
        ]
        header = '\t'.join(header) + '\n'
        tsvfile.write(header)
        for p, prof in datasets['faculties'].items():
            if prof['co_auts']:
                exp_prof = [
                    prof['first'], prof['last'], prof['init'], prof['i_last'],
                    prof['depts']
                ]
                for i, aut in prof['co_auts'].items():
                    exp_list = [
                        i, aut['cnt'], aut['name'], aut['raw_affil'],
                        aut['multi_affil'], ';'.join(aut['countries']),
                        aut['foreigner'], aut['foreign'], aut['sharif'],
                        aut['email_year'], aut['email'],
                    ]
                    years = {k: v for k, v in aut['papers'].items()}
                    dois = [v['doi'] for k, v in years.items()]
                    dois = ';'.join([item for sublist in dois for item in sublist])
                    years = ';'.join([str((k, v['cnt'])) for k, v in years.items()])

                    exp_list.append(years)
                    exp_list.append(dois)

                    exp_text = exp_prof + exp_list
                    exp_text = map(lambda item: str(item), exp_text)
                    exp_text = '\t'.join(exp_text) + '\n'
                    tsvfile.write(exp_text)