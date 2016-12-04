import subprocess as sp
import json

def run_dig(hostnames, output_filename, dns_query_server=None):
    
    with open(hostname_filename, 'r+') as f:
        hostnames = f.read().split()
    
    #Part 1 - run Popen and put into output_string
    
    output_string = ''

    for host in hostnames:
        num = 0
        while num < 5:
            if dns_query_server:
                shell_args = ['dig', host, dns_query_server]
            else:
                shell_args = ['dig', '+trace', '+tries=1', '+nofail', host]
               
            pipe = sp.Popen(shell_args, stdout=sp.PIPE, stderr=sp.STDOUT)
            out_string = pipe.communicate()[0]
            output_string = output_string + out_string + '=====\n'
            num += 1

    #Part 2 - parse output_string and put into json
    
    resolves = output_string.split('=====')

    resolves = [r for r in resolves if r != '' and r != ' ' and r != '\n']
    master_string = []

    for r in resolves:
        temp = r.split('\n')
        temp = [t for t in temp if t != '' and t != '\n']
#        temp = [t for t in temp if '=' not in t or 'tries' in t]
        print(len(temp))
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

    with open(output_filename, 'w+') as f2:
        json.dump(master_string, f2)

run_dig(['google.com', 'facebook.com'], 'dig_trial.json')
