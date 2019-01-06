from fuzzy_func2 import *
# analyze_auts('', '', 2018, 'papers.db', datasets, 80, True)

fac = {}
with io.open('scopus_ids.txt', 'r', encoding='UTF-16') as import_file:
    reader = csv.DictReader(import_file, dialect='excel-tab')
    for row in reader:
        if row['ids']:
            fac[row['sharif_id']] = row['ids']
            fac
        else:
            fac[row['sharif_id']] = ''
        print(fac[row['sharif_id']])
    # for k,v in datasets['faculties'].items():
    #     for i in v['scopus']:
