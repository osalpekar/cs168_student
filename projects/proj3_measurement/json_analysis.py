import json

def ping_response(json_file):
    
    with open(json_file, 'r+') as f:
        ping_dict = json.load(f)

    no_response = 0
    
    for host in ping_dict:
        if ping_dict[host]["drop_rate"] == 100.0:
            no_response += 1

    return no_response

def failed_ping(json_file):

    with open(json_file, 'r+') as f:
        ping_dict = json.load(f)
    
    num_fails = 0
    
    for host in ping_dict:
        if ping_dict[host]["drop_rate"] != 0.0:
            num_fails += 1
    
    return num_fails


if __name__ == "__main__":
    json_file = 'rtt_a_agg.json'
    ping_resp = ping_response(json_file)
    fail_ping = failed_ping(json_file)

    print('Websites not responding to pings ' + str(ping_resp) + '%')
    print('Websites with atleast 1 failed ping ' + str(fail_ping) + '%')
