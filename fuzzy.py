import os, csv, io
from collections import OrderedDict
from fuzzy_func2 import *# analyze_auts, corr_aut, paper_check, exp_emails, db_handler, splitter, aut_country, aut_dept, sharif_depts, dept_alias, datasets
# analyze_auts('', '', 2018, 'papers.db', datasets, 80, True)

analyze_co_auts('', 0, 2018, 'papers.db', datasets,
    dept_alias, sharif_depts, cutoff=80, exp_name='simchi.txt')