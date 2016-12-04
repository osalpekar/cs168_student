import subprocess as sp
import json
import numpy as np
import matplotlib.pyplot as plot

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    
    
    with open(hostname_filename, 'r+') as f:
        hostnames = f.read().split()
    
    #Part 1 - run Popen and put into output_string
    
    output_string = ''

    for host in hostnames:
        num = 0
        while num < 5:
            if dns_query_server:
                server = '@' + dns_query_server
                shell_args = ['dig', host, server]
            else:
                shell_args = ['dig', '+trace', '+tries=1', '+nofail', host]
               
            pipe = sp.Popen(shell_args, stdout=sp.PIPE, stderr=sp.STDOUT)
            out_string = pipe.communicate()[0]
            output_string = output_string + out_string + '=====\n'
            num += 1

    #Part 2 - parse output_string and put into json
    if not dns_query_server:    
        resolves = output_string.split('=====')

        resolves = [r for r in resolves if r != '' and r != ' ' and r != '\n']
        master_string = []

        for r in resolves:
            temp = r.split('\n')
            temp = [t for t in temp if t != '' and t != '\n']
    #        temp = [t for t in temp if '=' not in t or 'tries' in t]
            temp2 = temp[0].split()
            name = temp2[len(temp2) - 1]

            if 'timed out' in r:
                success = False
            else:
                success = True

            if not success:
                master_string.append({"Name": name, "Success": success})
            else:
                queries_list = []
                queries = r.split(';;')
                queries = [q for q in queries if q != '']
                queries = queries[1:]
                q_index = 0

                while q_index < len(queries) - 1:
                    temp3 = queries[q_index+1].split('\n')
                    temp4 = temp3[0].split()
                    time = temp4[-2]

                    ans = queries[q_index].split('\n')
                    ans = [a for a in ans if a != '']
                    ans = ans[1:]
                    answers = []

                    for a in ans:
                        values = a.split('\t')
                        values = [v for v in values if v != '']
                        answers.append({"Queried name": values[0], "Data": values[-1], "Type": values[-2], "TTL": values[1]})

                    queries_list.append({"Time": time, "Answers": answers})
                    q_index += 1

            master_string.append({"Name": name, "Success": success, "Queries": queries_list})

    else:
        
        resolves = output_string.split('=====')

        resolves = [r for r in resolves if r != '' and r != ' ' and r != '\n']
        master_string = []
        for r in resolves:
            if 'timed out' in r:
                success = False
            else:
                success = True
            
            lines = r.split(';;')
            temp = lines[0].split()
            name = temp[-2]
            
            if not success:
                master_string.append({"Name": name, "Success": success})
            else:
                temp2 = lines[7].split()
                time = temp2[-2]
                temp3 = lines[6].split()
                master_string.append({"Name": name, "Success": success, "Queries": [{"Time": time, "Answers": 
                    [{"Queried name": temp3[2], "Data": temp3[6], "Type": temp3[5], "TTL": temp3[3]}]}]})
                

    with open(output_filename, 'w+') as f2:
        json.dump(master_string, f2)

def get_average_ttls(filename):
    
    with open(filename, 'r+') as f:
        json_list = json.load(f)
    
    root_ttl = 0
    root_count = 0
    tld_ttl = 0
    tld_count = 0
    other_ttl = 0
    other_count = 0
    a_ttl = 0
    a_count = 0

    for dicts in json_list:
        queries = dicts["Queries"]

        for query in queries:

            if query == queries[0]:
                root_count += len(query["Answers"])
                for element in query["Answers"]:
                    root_ttl += int(element["TTL"])

            elif query == queries[1]:
                tld_count += len(query["Answers"])
                for element in query["Answers"]:
                    tld_ttl += int(element["TTL"])
            
            elif query == queries[len(queries) - 1]:
                a_count += len(query["Answers"])
                for element in query["Answers"]:
                    a_ttl += int(element["TTL"])

            else:
                other_count += len(query["Answers"])
                for element in query["Answers"]:
                    other_ttl += int(element["TTL"])
               
    return [float(root_ttl/root_count), float(tld_ttl/tld_count), float(other_ttl/other_count), float(a_ttl/a_count)]

def get_average_times(filename):
    

    with open(filename, 'r+') as f:
        json_list = json.load(f)
        
    a_time = 0
    a_count = 0
    other_time = 0
    other_count = 0

    for dicts in json_list:
        for item in dicts["Queries"]:
            end = len(dicts["Queries"]) - 1
            if item == dicts["Queries"][end]:
                a_time += item["Time"]
                a_count += 1
            else:
                other_time += item["Time"]
                other_count += 1
    
    return [other_time/other_count, a_time/a_count]


def generate_time_cdfs(json_filename, output_filename):

    with open(json_filename, 'r+') as f:
        json_list = json.load(f)
    
    total_times = []
    a_times = []

    for dicts in json_list:
        for item in dicts["Queries"]:
            end = len(dicts["Queries"]) - 1
            if item == dicts["Queries"][end]:
                a_times.append(int(item["Time"]))
            else:
                total_times.append(int(item["Time"]))

    ax = plot.subplot(111)
    plot.grid()
    plot.xlabel("Time (seconds)")
    plot.ylabel("Cumulative Percentage (%)")

    sort_total = np.sort(total_times)
    sort_a = np.sort(a_times)
    p_tot = len(sort_total) + 1
    p_a = len(a_times) + 1
    rng_tot = np.arange(float(p_tot)) * 1/(p_tot-1)
    rng_a = np.arange(float(p_a)) * 1/(p_a-1)

    plot.step(np.concatenate([sort_total, sort_total[[-1]]]), rng_tot, label = 'Total time')
    plot.step(np.concatenate([sort_a, sort_a[[-1]]]), rng_a, label = 'Final Request')
#    rng_tot = np.arange(float(p_tot-1)) * 1/(p_tot-2)
#    rng_a = np.arange(float(p_a-1)) * 1/(p_a-2)

#    plot.step(sort_total, rng_tot, label = 'Total time')
#    plot.step(sort_a, rng_a, label = 'Final Request')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plot.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plot.savefig(output_filename)


def count_different_dns_responses(filename1, filename2):
    
    with open(filename1, 'r+') as f:
        json_list1 = json.load(f)
    
    with open(filename2, 'r+') as f:
        json_list2= json.load(f)
    
    num_changes1 = 0
    num_changes2 = 0

    site_dict1 = {}
    site_dict2 = {}
    name_list = []
    
    for dicts in json_list1:
        name_list.append(dicts["Name"])
    
    unique_names = list(set(name_list))
    
    for name in unique_names:
        site_dict1[name] = []

    for dicts in json_list1:
        if dicts["Success"]:
            answers = dicts["Queries"][-1]["Answers"]
            inlist = []
            for answer in answers:
                if answer["Type"] == 'A' or answer["Type"] == 'CNAME':
                    inlist.append(answer["Data"])

            name = dicts["Name"]
            site_dict1[name].append(inlist)
   
    for key in site_dict1:
        site_dict2[key] = []
        for element in site_dict1[key]:
            site_dict2[key].append(element)

    for dicts in json_list2:
        if dicts["Success"]:
            answers = dicts["Queries"][-1]["Answers"]
            inlist = []
            for answer in answers:
                if answer["Type"] == 'A' or answer["Type"] == 'CNAME':
                    inlist.append(answer["Data"])

            name = dicts["Name"]
            site_dict2[name].append(inlist)


    for key in site_dict1:
        bool_list = [set(site_dict1[key][0]) == set(x) for x in site_dict1[key]]
        if False in bool_list:
            num_changes1 += 1

    for key in site_dict2:
        bool_list = [set(site_dict2[key][0]) == set(x) for x in site_dict2[key]]
        if False in bool_list:
            num_changes2 += 1
    return num_changes1, num_changes2
#    print num_changes1, num_changes2



#if __name__ == "__main__":
    #run_dig('alexa_top_100', 'dns_output_1.json')
    #print 'average ttls are:' 
    #print get_average_ttls('dns_output_1.json')
    #generate_time_cdfs('dns_output_1.json', 'dns_b_cdf.png')
    
    #for part c - comment the above out
#    run_dig('alexa_top_100', 'dns_output_2.json')
#    print count_different_dns_responses('dns_output_1.json', 'dns_output_2.json')

    #for part d - comment the above out
#    run_dig('alexa_top_100', 'dns_output_other_server.json', '82.98.162.251')
#    print count_different_dns_responses('dns_output_1.json', 'dns_output_other_server.json')
