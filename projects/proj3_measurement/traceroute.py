import subprocess as sp
import json
import time


def run_traceroute(hostnames, num_packets, output_filename):
   
    output_string = ''

    for h in hostnames:
        shell_args = ['traceroute', '-a', '-q', str(num_packets), h]
        pipe = sp.Popen(shell_args, stdout=sp.PIPE, stderr = sp.STDOUT)
        out_string = pipe.communicate()[0]
        output_string = output_string + out_string + '\n\n'
    
    with open(output_filename, 'w+') as f:
        f.write(output_string)


def parse_traceroute(raw_traceroute_filename, output_filename):
    with open(raw_traceroute_filename, 'r+') as f:
        hosts = f.read().split('traceroute')

    hosts = hosts[1:] #1 huge string for google and 1 huge string for fb
    hop_dict = {}
    hop_dict["timestamp"] = time.time()
    for h in hosts:
        hops = h.split('\n') #hops is a list with lines
        temp = hops[0].split()
        host_name = temp[1]
        hops = hops[1:]
        hops = [h for h in hops if h != '' and h != ' ']
        i = 1
        hop_dict[host_name] = []
        for line in hops:
            elem = line.split()
            length = len(elem) - 1
            failed = True
            
            shift = 0
            if elem[0] == str(i):
                i+=1
                
                for a in range(length):
                    if elem[a+1] == '*':
                        failed = True and failed
                        shift += 1
                    else:
                        failed = False
                        break
            
                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[3 + shift]) - 1
                    ip = elem[3 + shift][1:len_ip] #now 2
                    len_asn = len(elem[1 + shift]) - 1
                    asn = elem[1 + shift][1:len_asn] #now 3
                    hop_dict[host_name].append([{"name": elem[2 + shift], "ip": ip, "ASN": asn}]) #now 1
                else:
                    hop_dict[host_name].append([{"name": None, "ip": None, "ASN": None}])
            
            else:
                
                for a in range(length):
                    if elem[a] == '*':
                        failed = True and failed
                        shift += 1
                    else:
                        failed = False
                        break
                
                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[2 + shift]) - 1
                    ip = elem[2 + shift][1:len_ip] #now 1
                    len_asn = len(elem[0 + shift]) - 1
                    asn = elem[0 + shift][1:len_asn] #now 2
                    hop_dict[host_name][index].append({"name": elem[1 + shift], "ip": ip, "ASN": asn}) #now 0
                else:
                    hop_dict[host_name][index].append({"name": None, "ip": None, "ASN": None})

    with open(output_filename, 'a+') as f2:
        #json.dump(hop_dict, f2)
        f2.write('{}\n'.format(json.dumps(hop_dict)))




def parse_traceroute_backwards(raw_traceroute_filename, output_filename):
    with open(raw_traceroute_filename, 'r+') as f:
        hosts = f.read().split('\n\n')

    #hosts = hosts[1:] #1 huge string for google and 1 huge string for fb
    hop_dict = {}
    hop_dict["timestamp"] = time.time()
    for h in hosts:
        hops = h.split('\n') #hops is a list with lines
        #temp = hops[0].split()
        host_name = hops[0]
        hops = hops[1:]
        hops = [h for h in hops if h != '' and h != ' ']
        i = 1
        hop_dict[host_name] = []
        for line in hops:
            elem = line.split()
            length = len(elem) - 1
            failed = True
            
            shift = 0
            if elem[0] == str(i):
                i+=1
                
                for a in range(length):
                    if elem[a+1] == '*':
                        failed = True and failed
                        shift += 1
                    else:
                        failed = False
                        break
            
                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[2 + shift]) - 1
                    ip = elem[2 + shift][1:len_ip] 
                    len_asn = len(elem[3 + shift]) - 1
                    asn = elem[3 + shift]
                    if '[' in asn:
                        asn = asn[1:len_asn]
                    else:
                        asn = None
                    hop_dict[host_name].append([{"name": elem[1 + shift], "ip": ip, "ASN": asn}]) 
                else:
                    index = len(hop_dict[host_name]) - 1
                    hop_dict[host_name].append([{"name": None, "ip": None, "ASN": None}])
            
            else:
                
                for a in range(length):
                    if elem[a] == '*':
                        failed = True and failed
                        shift += 1
                    else:
                        failed = False
                        break
                
                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[1 + shift]) - 1
                    ip = elem[1 + shift][1:len_ip] #now 1
                    len_asn = len(elem[2 + shift]) - 1
                    asn = elem[2 + shift]
                    if '[' in asn:
                        asn = asn[1:len_asn]
                    else:
                        asn = None
                    hop_dict[host_name][index].append({"name": elem[0 + shift], "ip": ip, "ASN": asn}) #now 0
#                else:
#                    index = len(hop_dict[host_name]) - 1
#                    hop_dict[host_name][index].append({"name": None, "ip": None, "ASN": None})

    with open(output_filename, 'a+') as f2:
        f2.write('{}\n'.format(json.dumps(hop_dict)))



'''
#script for experiment a
if __name__ == "__main__":
    hostnames = ['google.com', 'facebook.com', 'www.berkeley.edu', 'allspice.lcs.mit.edu', 'todayhumor.co.kr',
        'www.city.kobe.lg.jp', 'www.vutbr.cz', 'zanvarsity.ac.tz'] 
    num_packets = 5
    output_filename = 'tr_a.txt'
    run_traceroute(hostnames, num_packets, output_filename)
    parse_traceroute('tr_a.txt', 'tr_a.json')

#script for experiment b part 1
if __name__ == "__main__":
    hostnames = ['tpr-route-server.saix.net', 'route-server.ip-plus.net', 'route-views.oregon-ix.net', 'route-views.on.bb.telus.com']
    num_packets = 5
    output_filename = 'tr_b.txt'
    run_traceroute(hostnames, num_packets, output_filename)
    parse_traceroute('tr_b.txt', 'tr_b.json')
'''
'''
#script for experiment b part 2
if __name__ == "__main__":
    parse_traceroute_backwards('tr_b2.txt', 'tr_b.json')
'''
