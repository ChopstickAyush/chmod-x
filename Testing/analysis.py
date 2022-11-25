#!/usr/bin/python3

from functools import cmp_to_key
import numpy as np
import os

def less(x, y) : 
        if len(x.split(' ')) >= 2 and len(y.split(' ')) >= 2 :
            t1 = x.split(' ')[-2]
            t2 = y.split(' ')[-2]
            return int(t1) - int(t2)
        return 0


def sort(subjects) :    

    sortedDict = sorted(subjects, key = cmp_to_key(less))
    return sortedDict


def merge(files):
    merged = []
    for f in files:
        my_file = open(f, "r")
        data = my_file.read()
        data_into_list = data.split("\n")
        merged.extend(data_into_list)
        my_file.close()
    x = sort(merged)
    return x
lst = os.listdir("log")
for i in range(len(lst)) :
    lst[i] = "log/" + lst[i]
print(lst)
sorted_messages = merge(lst)

def latency(messages, start_id, end_id) :
    latency = 0 
    num = 0
    for i in messages : 
        if i.split(' ')[-1] == 's' and int(i.split(' ')[1])>=start_id and int(i.split(' ')[1]) < end_id:
            for j in messages : 
                if j.split(' ')[-1] == 'r' and i.split(' ')[:3] == j.split(' ')[:3] :
                    latency += np.abs(int(j.split(' ')[-2]) - int(i.split(' ')[-2]))
                    num += 1
    if num == 0 : 
        print("Not enough data!")
        return 0
    
    return latency/num

print(latency(sorted_messages, 0, 1000))

def throughput(messages, time_window) :

    start_time = int(messages[0].split(" ")[-2]) + 100

    # Considering average over 10 intervals separated by 100ms
    starts = list(range(start_time, start_time + time_window * 10, time_window))
    num_input = 0
    num_output = 0
    input_throughputs = []
    output_throughputs = []

    for start in starts : 
        end_time = start + time_window 

        for i in messages :
            if len(i.split(' ')) >= 2:  
                if int(i.split(' ')[-2]) >= start and int(i.split(' ')[-2]) <= end_time : 
                    if i.split(' ')[-1] == 'r':
                        num_input += 1
                    else : 
                        num_output += 1
        
        input_throughputs.append(num_input)
        output_throughputs.append(num_output)
    
    input_avg = 0 
    count = 0
    for i in input_throughputs : 
        input_avg += i 
        count += 1
    input_avg = input_avg/count

    output_avg = 0 
    count = 0
    for i in output_throughputs : 
        output_avg += i 
        count += 1
    output_avg = output_avg/count

    return [input_avg, output_avg]

throughputs = throughput(sorted_messages, 1000)
print(throughputs)