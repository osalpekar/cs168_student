import json

def stable(infile):
    with open(infile, 'r+') as f:
        json_list = json.load(f)

    #runs = json_list.split('\n')

    site_names = ['google.com', 'facebook.com', 'www.berkeley.edu', 'allspice.lcs.mit.edu', 'todayhumor.co.kr',
         'www.city.kobe.lg.jp', 'www.vutbr.cz', 'zanvarsity.ac.tz']

    run1 = json_list[0]
    site_dict = {}
    for name in site_names:
        bool_list = [run1[name] == runx[name] for runx in json_list]
        site_dict[name] = bool_list.count(False)

    for key in site_dict:
        print key + '\t' + str(site_dict[key])


stable('count_stable.json')
