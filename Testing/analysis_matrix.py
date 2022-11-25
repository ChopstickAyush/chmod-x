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
print("a: 351 hi 1669388971546 r" in sorted_messages)

def num_zeros(l) : 
    for i in l : 
        if i == 0 : return False 
    return True

# def latency(messages, start_idx, end_idx, num_clients) :
#     cols = end_idx - start_idx
#     rows = num_clients
#     data = [[[0]*num_clients]*cols]*rows
#     latency = 0
#     num_messages = 0
#     counter = 0
#     clients = {}
#     print(data[0][171])
#     for i in messages : 
        
#         sender = i.split(' ')[0][:-1]
#         if sender not in clients : 
#             clients[sender] = counter
#             counter += 1
#         sender = clients[sender]
        
#         if len(i.split(' ')) <= 1 : continue
#         id = int(i.split(' ')[1])
#         if id >= start_idx and id < end_idx :
            
#             if i.split(' ')[-2] is not None : 
#                 for k in range(num_clients) : 
                    
#                     if data[sender][id-start_idx] == [0, 0, 0, 0] :
#                         print(sender, id-start_idx)
#                         data[sender][id-start_idx][k] = int(i.split(' ')[-2])
#                         print(data)
#                         return 
#                         break
                    
#             if num_zeros(data[sender][id-start_idx]) :
#                 num_messages += 1
#                 for j in range(1, num_clients) : 
#                     latency += np.abs(data[sender][id-start_idx][j] - data[sender][id-start_idx][0])
#                     #print(id, j, latency,data[sender][id-start_idx])
#     return latency/num_messages
# lat = latency(sorted_messages, 180, 500, 4)
# print(lat)