import time

def trace_parser(infile):
    with open(infile, 'r+') as f:
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
            failed = False
            if elem[0] == str(i):
                i+=1
                
                for a in range(length):
                    if elem[a+1] == '*':
                        failed = True
                    else:
                        failed = False

                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[3]) - 1
                    ip = elem[3][1:len_ip]
                    len_asn = len(elem[1]) - 1
                    asn = elem[1][1:len_asn]
                    hop_dict[host_name].append([{"name": elem[2], "ip": ip, "ASN": asn}])
                else:
                    hop_dict[host_name].append([{"name": None, "ip": None, "ASN": None}])

            else:

                for a in range(length):
                    if elem[a] == '*':
                        failed = True
                    else:
                        failed = False
                
                if not failed:
                    index = len(hop_dict[host_name]) - 1
                    len_ip = len(elem[2]) - 1
                    ip = elem[2][1:len_ip]
                    len_asn = len(elem[0]) - 1
                    asn = elem[0][1:len_asn]
                    hop_dict[host_name][index].append({"name": elem[1], "ip": ip, "ASN": asn})
                else:
                    hop_dict[host_name][index].append({"name": None, "ip": None, "ASN": None})

    print(hop_dict)
    '''
    with open(output_filename, 'w+') as f2:
        json.dump(hop_dict, f2)
    '''








trace_parser('traceroute_output.txt')
