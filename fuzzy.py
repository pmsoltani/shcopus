from fuzzy_func2 import analyze_auts, db_handler, splitter, aut_country, aut_dept, sharif_depts, dept_strings, datasets
# analyze_auts('', '', 2018, 'papers.db', datasets, 80, True)

import os, csv, io
from collections import OrderedDict

papers = db_handler('papers.db', '', '', 2018, add_keys=[('skip', False)])

db_name = 'Faculties'
profs = OrderedDict()
with open(
    os.path.join('datasets', db_name + '.csv'), encoding='UTF-8-sig'
) as import_file:

    reader = csv.DictReader(import_file)
    for row in reader:
        profs[row['ID']] = {
            'first': row['First En'],
            'last': row['Last En'],
            'init': row['Initial En'],
            'i_last': row['Initial En'] + ' ' + row['Last En'],
            'depts': row['Dept'],
            'co_auts': {}, 'cnt': 0,
        }
        if row['Scopus']:
            profs[row['ID']]['scopus'] = list(
                map(lambda item: eval(item), row['Scopus'].split(';'))
            )
        else:
            profs[row['ID']]['scopus'] = []

for p, prof in profs.items():
    if not prof['scopus']:
        continue
    for i in papers:
        if i['skip']:
            continue
        if type(i['auts_id']) == str:
            i['auts_id'] = splitter(i['auts_id'], ';', out_type='list')
            i['auts'] = splitter(
                i['auts'], ',', vacuum=lambda item: len(item.strip()) > 3)
            auts_affils = splitter(i['auts_affils'], ';', out_type='list')
            # Ignoring papers with too many authors involved!
            if len(i['auts']) > 30:
                i['skip'] = True
                continue
            if len(i['auts']) != len(i['auts_id']):
                i['skip'] = True
                continue
            if len(auts_affils) != len(i['auts_id']):
                i['skip'] = True
                continue

            temp = OrderedDict()
            for cnt, aut in enumerate(auts_affils):
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
                    temp[cnt]['countries'],
                    temp[cnt]['multi_affil'],
                    temp[cnt]['foreigner'],
                    temp[cnt]['foreign'],
                    temp[cnt]['affils'],
                ] = aut_country(aut_split, datasets['countries'])
                if not temp[cnt]['foreigner']:
                    [
                        temp[cnt]['sharif'],
                        temp[cnt]['depts'],
                    ] = aut_dept(
                        temp[cnt]['affils'], dept_strings,
                        sharif_depts, 80, 'sharif'
                    )
            i['auts_affils'] = temp
        if any(scop[0] in i['auts_id'] for scop in prof['scopus']):
            co_auts = [item for item in i['auts_id'] if item not in prof['scopus'][0]]
            for aut in co_auts:
                idx = i['auts_id'].index(aut)
                if aut not in prof['co_auts'].keys():
                    prof['co_auts'][aut] = {
                        'cnt': 0,
                        'name'       : i['auts_affils'][idx]['init'] + ' ' + i['auts_affils'][idx]['last'],
                        'raw_affil'  : i['auts_affils'][idx]['raw_affil'],
                        'multi_affil': i['auts_affils'][idx]['multi_affil'],
                        'countries'  : i['auts_affils'][idx]['countries'],
                        'foreigner'  : i['auts_affils'][idx]['foreigner'],
                        'foreign'    : i['auts_affils'][idx]['foreign'],
                        'affils'     : i['auts_affils'][idx]['affils'],
                        'sharif'     : i['auts_affils'][idx]['sharif'],
                    }
                if i['year'] not in prof['co_auts'][aut].keys():
                    prof['co_auts'][aut][i['year']] = {'cnt': 0, 'doi': []}
                
                prof['cnt'] += 1

                prof['co_auts'][aut]['cnt'] += 1
                prof['co_auts'][aut][i['year']]['cnt'] += 1
                prof['co_auts'][aut][i['year']]['doi'].append(i['doi'])
    # prof['co_auts'] = {k: v for k, v in prof['co_auts'].items() if v['cnt'] > 1}

with io.open('co_aut.txt', 'w', encoding='UTF-16') as tsvfile:
    header = [
        'First', 'Last', 'Init', 'i_last', 'Depts',
        'co_auts_id', 'Total', 'Name', 'Raw Affil', 'Multi Affil',
        'Countries', 'Foreigner', 'Foreign Affil', 'Sharif', 'Years', 'DOIs',
    ]
    header = '\t'.join(header) + '\n'
    tsvfile.write(header)
    for p, prof in profs.items():
        if prof['co_auts']:
            exp_prof = [
                prof['first'], prof['last'], prof['init'], prof['i_last'],
                prof['depts']
            ]
            for i, aut in prof['co_auts'].items():
                exp_list = [
                    i, aut['cnt'], aut['name'], aut['raw_affil'], aut['multi_affil'],
                    ';'.join(aut['countries']), aut['foreigner'], aut['foreign'],
                    aut['sharif'],
                ]
                years = {k: v for k, v in aut.items() if '20' in k}
                dois = [v['doi'] for k, v in years.items()]
                dois = ';'.join([item for sublist in dois for item in sublist])
                years = ';'.join([str((k, v['cnt'])) for k, v in years.items()])

                exp_list.append(years)
                exp_list.append(dois)

                exp_text = exp_prof + exp_list
                exp_text = map(lambda item: str(item), exp_text)
                exp_text = '\t'.join(exp_text) + '\n'
                tsvfile.write(exp_text)