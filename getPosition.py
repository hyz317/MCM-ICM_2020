import re
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

dict = {}
num = 0
G = nx.Graph()


def store(player, posx, posy):
    global dict, num
    if not posx:
        return
    if player in dict:
        dict[player].append((eval(posx), eval(posy)))
    elif num <= 10:
        dict[player] = [(eval(posx), eval(posy))]
        num += 1


with open("fullevents.csv", 'r') as f:
    for i in range(1522):
        ls = f.readline().split(',')
        if ls[1] == "Huskies":
            if ls[3] == '':
                store(ls[2], ls[8], ls[9])
            else:
                store(ls[2], ls[8], ls[9])
                store(ls[3], ls[10], ls[11][:-1])

print(dict)

mean_x_ls = []
mean_y_ls = []

pos_ls = []
id_dict = {}
name2id = {}
temp_num = -1


for member in dict:
    print(member)
    temp_num += 1

    if member[8] == 'G':
        for i in range(dict[member].__len__()):
            if dict[member][i][0] == 0 and dict[member][i][1] == 0:
                dict[member][i] = (7, 50)

    x_ls = []
    y_ls = []
    for i in dict[member]:
        x_ls.append(i[0])
        y_ls.append(i[1])

    mean_x_ls.append(np.mean(x_ls))
    mean_y_ls.append(np.mean(y_ls))

    name2id[member] = temp_num
    id_dict[temp_num] = member
    pos_ls.append((np.mean(x_ls), np.mean(y_ls)))

    # if member == "Huskies_D5":
    #    plt.plot(x_ls, y_ls, "mo")
    '''
    if member[8] == 'D':
        plt.plot([np.mean(x_ls)], [np.mean(y_ls)], "bo")
    elif member[8] == 'M':
        plt.plot([np.mean(x_ls)], [np.mean(y_ls)], "go")
    elif member[8] == 'F':
        plt.plot([np.mean(x_ls)], [np.mean(y_ls)], "ro")
    elif member[8] == 'G':
        plt.plot([np.mean(x_ls)], [np.mean(y_ls)], "yo")
    '''
# plt.plot(mean_x_ls, mean_y_ls, "mo")
plt.xlim(0, 100)
plt.ylim(0, 100)

with open("data.csv", 'r') as f:
    for i in f.readlines():
        ls = i.split(',')

        if ls[3][:-1] != '0':
            if ls[1][1:-1] in name2id and ls[2][1:-1] in name2id:
                G.add_edge(name2id[ls[1][1:-1]], name2id[ls[2][1:-1]], weight=eval(ls[3][:-1]))
                print(eval(ls[3][:-1]))

nx.draw_networkx_edges(G, pos_ls, width=[float(d['weight'] / 5) for (u, v, d) in G.edges(data=True)])
nx.draw_networkx_nodes(G, pos_ls)
nx.draw_networkx_labels(G, id_dict)

plt.show()
