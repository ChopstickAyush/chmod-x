from functools import cmp_to_key
import numpy as np

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
    
    
sorted_messages = merge(["log/a_log.txt","log/b_log.txt","log/c_log.txt","log/d_log.txt"])

def latency(messages, start_id, end_id) :
    latency = 0 
    num = 0
    for i in messages : 
        if i.split(' ')[-1] == 's' and int(i.split(' ')[1])>=start_id and int(i.split(' ')[1]) < end_id:
            for j in messages : 
                if j.split(' ')[-1] == 'r' and i.split(' ')[:3] == j.split(' ')[:3] :
                    latency += np.abs(int(j.split(' ')[-2]) - int(i.split(' ')[-2]))
                    print(np.abs(int(j.split(' ')[-2]) - int(i.split(' ')[-2])))
                    num += 1
    return latency/num

print(latency(sorted_messages, 500, 1000))

