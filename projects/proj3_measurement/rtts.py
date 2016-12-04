import subprocess as sp
import json
import numpy as np
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf

def run_ping(hostnames, num_packets, 
        raw_ping_output_filename, aggregated_ping_output_filename):
    
    host_rtt = {}
    drop_dict = {}
    host_agg_dict = {}
    cumulative_agg_dict = {}
    #run the ping shell command

    for h in hostnames:
        
        shell_args = ['ping', '-c', str(num_packets), h]
        pipe = sp.Popen(shell_args, stdout=sp.PIPE)
        out_string = pipe.communicate()[0]
        #shell_string = "ping -c " + str(num_packets) + " " + h
        #out_string = sp.check_output(shell_string, shell=True)
        split_shell_output = out_string.split()
        
        split_lines = out_string.split('\n')
        split_lines = split_lines[1:]
        split_lines = [l for l in split_lines if l != '']
        split_lines = [l for l in split_lines if 'icmp' in l]

        rtts = []
        line_num = 0
        while line_num < num_packets - 1:
            if 'Request timeout' not in split_lines[line_num]:
                temp1 = split_lines[line_num].split('time=')
                temp2 = temp1[1].split()
                rtts.append(float(temp2[0]))
            else:
                rtts.append(-1)
        
            line_num += 1
        
        host_rtt[h] = rtts
        
        drop_list = [s for s in split_shell_output if "%" in s]
        drop_format = [s.split("%") for s in drop_list]
        drop_pct = float(drop_format[0][0])
        drop_dict[h] = drop_pct
    
    with open(raw_ping_output_filename, 'w+') as f:
        json.dump(host_rtt, f)
    
    for host in host_rtt:
        rtt_list = host_rtt[host]
        new_rtt_list = [el for el in rtt_list if el != -1]
        if len(new_rtt_list) == 0:
            list_max = -1
            list_median = -1
            list_drop = 100.0
        else:
            list_max = np.around(np.amax(new_rtt_list), decimals=3)
            list_median = np.around(np.median(new_rtt_list), decimals=3)
            list_drop = float(len(rtt_list) - len(new_rtt_list))/float(len(rtt_list))*100.0
        cumulative_agg_dict[host] = {}
        cumulative_agg_dict[host]["drop_rate"] = list_drop
        cumulative_agg_dict[host]["max_rtt"] = list_max
        cumulative_agg_dict[host]["median_rtt"] = list_median

    with open(aggregated_ping_output_filename, 'w+') as f2:
        json.dump(cumulative_agg_dict, f2)

def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename):
    
    with open(agg_ping_results_filename, 'r') as f:
        agg_dict = json.load(f)
    
    rtt_list = []
    for host in agg_dict:
        median = agg_dict[host]["median_rtt"]
        if median != -1:
            rtt_list.append(median)
    
    ax = plot.subplot(111)
    sort_rtt = np.sort(rtt_list)
    p = len(sort_rtt) + 1
    rng = np.arange(float(p)) * 1/(p-1)
    plot.step(np.concatenate([sort_rtt, sort_rtt[[-1]]]), rng, label = "Median RTTs")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.78, box.height])
    plot.legend(loc='center left', bbox_to_anchor=(1, 0.5)) 
    plot.grid() 
    plot.xlabel("Time (seconds)") 
    plot.ylabel("Cumulative Percentage (%)")
    plot.savefig(output_cdf_filename)
    #plot.show()
    #plot.close()

def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):
    #put it in one file - the example will run with 4 hosts so
    #there will be 4 lines in one file
    with open(raw_ping_results_filename, 'r') as f:
        raw_dict = json.load(f)
    
    ax = plot.subplot(121)
    plot.grid() 
    plot.xlabel("Time (seconds)") 
    plot.ylabel("Cumulative Percentage (%)")
    
    rtt_list = []
    for host in raw_dict:
        times = raw_dict[host]
        times = [t for t in times if t != -1]
        if len(times) == 0:
            continue
        sort_times = np.sort(times)
        p = len(sort_times) + 1
        rng = np.arange(float(p)) * 1/(p-1)
        plot.step(np.concatenate([sort_times, sort_times[[-1]]]), rng, label = host)
    #    plot.legend() 
        
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 1.5, box.height])
    plot.legend(loc='center left', bbox_to_anchor=(1, 0.5)) 
    plot.savefig(output_cdf_filename)
    #plot.show()
    #plot.close()

#Script for running experiment A
if __name__ == "__main__":
    f = open("alexa_top_100", 'r')
    host_list = f.read().split()
    hostnames = [h for h in host_list if h != ""]
    num_packets = 11
    raw_ping_output_filename = "rtt_a_raw.json"
    aggregated_ping_output_filename = "rtt_a_agg.json"
    run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename)
    plot_median_rtt_cdf(aggregated_ping_output_filename, "agg_a_cdf.png")

#Script for running experiment B
'''
if __name__ == "__main__":
    hostnames = ['google.com', 'todayhumor.co.kr', 'zanvarsity.ac.tz', 'taobao.com']
    num_packets = 501
    raw_ping_output_filename = "rtt_b_raw.json"
    aggregated_ping_output_filename = "rtt_b_agg.json"
    run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename)
    plot_ping_cdf(raw_ping_output_filename, 'raw_b_cdf.png')
    plot_median_rtt_cdf(aggregated_ping_output_filename, "agg_b_cdf.png")
'''
