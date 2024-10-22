import re
import math
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


def sigmoid(x):
    y = 1.0 / (1.0 + np.exp(-x))
    return y


def dijkstra(graph, src):
    # init
    visited = []
    distance = {src: 0}
    node = list(range(len(graph[0])))
    edges = []
    if src in node:
        node.remove(src)
        visited.append(src)
    else:
        return None
    for i in node:
        distance[i] = graph[src][i]
    prefer = src
    while node:
        _distance = float('inf')
        for i in visited:
            for j in node:
                if graph[i][j] > 0:
                    if _distance > distance[i] + graph[i][j]:
                        _distance = distance[j] = distance[i] + graph[i][j]
                        prefer = j
                        father = i
        visited.append(prefer)
        edges.append((father, prefer))
        # print(node)
        node.remove(prefer)
    return distance, edges


# read csv file.
def read():
    with open("fullevents.csv", 'r') as f:
        full_ls = []
        for i in f.readlines():
            ls = i[:-1].split(',')
            full_ls.append(ls)
    return full_ls


def getMatchData(match_id, data):
    ls = []
    for i in data:
        if i[0] == str(match_id):
            ls.append(i)
    return ls


# get a list of Huskies' members who has entered the court.
def getNameList(data):
    ls = []
    for i in data:
        if i[1] == "Huskies" and i[2] not in ls:
            ls.append(i[2])
    return ls


# get a empty 2-dimension dictionary, which is used to express gains of edges.
def getEmptyMatrix(name_list):
    dict = {}
    for i in name_list:
        dict_i = {}
        for j in name_list:
            dict_i[j] = 0
        dict[i] = dict_i
    return dict


# returns a dictionary from player name to presence time(a tuple).
def getTimeRangeDict(name_list, data):
    dict = {}

    second_half_time = math.ceil(eval(data[data.__len__() - 1][5]) / 60) * 60
    for i in range(data.__len__()):
        if data[i][4] == '2H':
            i -= 1
            first_half_time = math.ceil(eval(data[i][5]) / 60) * 60
            break

    up_ls = []
    down_ls = []
    time_ls = []

    for i in data:
        if i[1] == 'Huskies' and i[6] == 'Substitution':
            down_ls.append(i[2])
            up_ls.append(i[3])
            if i[4] == '1H':
                time_ls.append(eval(i[5]))
            else:
                time_ls.append(eval(i[5]) + first_half_time)

    for name in name_list:
        up_time = 0
        down_time = first_half_time + second_half_time
        for j in range(up_ls.__len__()):
            if name == up_ls[j]:
                up_time = time_ls[j]
            elif name == down_ls[j]:
                down_time = time_ls[j]
        dict[name] = (float(up_time), float(down_time))

    return dict


def getXMean(id_list, data):
    x_ls = []
    for i in id_list:
        x_ls.append(eval(data[i][8]))
        x_ls.append(eval(data[i][10]))
    return np.mean(x_ls)


# get stability reward
def stability(name_list, data):
    num = 0
    endnum = 0
    dict = getEmptyMatrix(name_list)

    while endnum < data.__len__() and num < data.__len__():
        pass_ls = []
        player_ls = []
        pass_num = 0
        duel_num = 0

        if data[num][6] != "Free Kick" and data[num][6] != "Pass":
            num += 1
            endnum += 1
            continue

        if data[num][1] != "Huskies":
            num += 1
            endnum += 1
            continue
        while endnum < data.__len__():
            if data[endnum][6] == "Free Kick" and data[endnum][1] == "Huskies" and duel_num < 3:
                endnum += 1
                duel_num = 0
            elif data[endnum][7] == "Acceleration" and data[endnum][1] == "Huskies" and duel_num < 3:
                endnum += 1
                duel_num = 0
            elif data[endnum][7] == "Touch" and data[endnum][1] == "Huskies" and duel_num < 3:
                endnum += 1
                duel_num = 0
            elif data[endnum][6] == "Pass" and data[endnum][1] == "Huskies" and duel_num < 3:
                pass_ls.append(endnum)
                if data[endnum][2] not in player_ls and data[endnum][3] != "":
                    player_ls.append((data[endnum][2], data[endnum][3]))
                if data[endnum][3] != "":
                    pass_num += 1
                endnum += 1
                # print(endnum)
                duel_num = 0
            elif data[endnum][6] == "Duel" and duel_num < 3:
                endnum += 1
                duel_num += 1
            elif pass_num < 3:
                num = endnum
                break
            else:
                # print("({0}, {1}) {2}".format(num+2, endnum+1, player_ls))
                mean = getXMean(pass_ls, data)
                for players in player_ls:
                    dict[players[0]][players[1]] += float(pow(max(mean - 30, 0), 2)) / 360
                    dict[players[1]][players[0]] += float(pow(max(mean - 30, 0), 2)) / 360
                    # print(float(pow(max(mean - 30, 0), 2)) / 3000)
                num = endnum
                break

    return dict


# get accuracy reward
def accuracy(name_list, data):
    dict = getEmptyMatrix(name_list)
    for i in data:
        if i[1] == "Huskies" and i[3] != "" and i[6] == "Pass":
            dict[i[2]][i[3]] += 1
            dict[i[3]][i[2]] += 1
    return dict


# get reward for difficulty
def difficulty(name_list, data):
    dict = getEmptyMatrix(name_list)
    for i in data:
        if i[1] == 'Huskies' and i[3] != "" and i[6] == 'Pass':
            dis = math.sqrt(pow((1.05 * (eval(i[8]) - eval(i[10]))), 2) + pow((0.68 * (eval(i[9]) - eval(i[11]))), 2))
            dis /= math.sqrt(105 * 105 + 68 * 68)
            pos = max((eval(i[8]) + eval(i[10])) / 2, 50) / 60 - 2 / 3
            dict[i[2]][i[3]] += (dis + 4 * pos)
            dict[i[3]][i[2]] += (dis + 4 * pos)
    return dict


# get extra product factor as compensation for short playing time
def personReward(time_dict):
    dict = {}
    for i in time_dict:
        time = float(time_dict[i][1] - time_dict[i][0]) / 60
        if time > 60:
            dict[i] = 1.0
        elif time > 10:
            dict[i] = pow(time - 60, 2) / 5000 + 1
        else:
            dict[i] = 1.5
    return dict


'''
def personPenalty1(name_list, data):
    dict = {}
    for name in name_list:
        dict[name] = 1.0

    for i in data:
        if i[1] == 'Huskies' and i[3] == "" and i[6] == 'Pass':
            if eval(i[8]) > 40:
                dict[i[2]] *= 1.0
            elif eval(i[8]) > 20:
                dict[i[2]] *= (0.75 + 0.25 / 20.0 * (eval(i[8]) - 20.0))
            else:
                dict[i[2]] *= 0.75

    return dict


def personPenalty2(name_list, data):
    dict = {}
    for name in name_list:
        dict[name] = 1.0

    for i in data:
        if i[1] == 'Huskies' and i[3] == "" and i[6] == 'Pass':
            dis = 4.0 * pow((eval(i[10]) - eval(i[8])), 2) + pow((eval(i[11]) - eval(i[9])), 2)
            if dis <= 500:
                dict[i[2]] *= (sigmoid(dis / 100.0 - 0.5) * 0.4 + 0.8)

    return dict
'''


# entropy method to get weight
def getWeight(dict1, dict2, dict3, lst):
    N = 0
    sum = 0
    e1 = 0
    for i in lst:
        for j in lst:
            if dict1[i][j] != 0:
                N += 1
                sum += dict1[i][j]
    for i in lst:
        for j in lst:
            if dict1[i][j] != 0:
                p = dict1[i][j] / sum
                dict1[i][j] = p * 100
                e1 += -(p * math.log(p))
    e1 /= math.log(N)
    e1 = 1 - e1

    N = 0
    sum = 0
    e2 = 0
    for i in lst:
        for j in lst:
            if dict2[i][j] != 0:
                N += 1
                sum += dict2[i][j]
    for i in lst:
        for j in lst:
            if dict2[i][j] != 0:
                p = dict2[i][j] / sum
                dict2[i][j] = p * 100
                e2 += -(p * math.log(p))
    e2 /= math.log(N)
    e2 = 1 - e2

    N = 0
    sum = 0
    e3 = 0
    for i in lst:
        for j in lst:
            if dict3[i][j] != 0:
                N += 1
                sum += dict3[i][j]
    for i in lst:
        for j in lst:
            if dict3[i][j] != 0:
                p = dict3[i][j] / sum
                dict3[i][j] = p * 100
                e3 += -(p * math.log(p))
    e3 /= math.log(N)
    e3 = 1 - e3

    sum = e1 + e2 + e3
    return e1 / sum, e2 / sum, e3 / sum, dict1, dict2, dict3


def evaluation(name_list, dict1, dict2, dict3, w1, w2, w3, time_dict):
    dict = getEmptyMatrix(name_list)
    for i in name_list:
        for j in name_list:
            dict[i][j] = time_dict[i] * time_dict[j] * (w1 * dict1[i][j] + w2 * dict2[i][j] + w3 * dict3[i][j])
            dict[j][i] = dict[i][j]
    return dict


def store(dict, player, posx, posy, num, MAXNUM):
    if not posx:
        return num
    if player in dict:
        dict[player].append((eval(posx), eval(posy)))
    elif num < MAXNUM:
        dict[player] = [(eval(posx), eval(posy))]
        num += 1
    return num


def getPos(name_list, data):
    num = 0
    dict = {}
    for ls in data:
        if ls[1] == "Huskies":
            if ls[3] == '':
                num = store(dict, ls[2], ls[8], ls[9], num, 30)
            else:
                num = store(dict, ls[2], ls[8], ls[9], num, 30)
                # num = store(dict, ls[3], ls[10], ls[11][:-1], num, 11)

    if "Huskies_Gate" in name_list:
        dict["Huskies_Gate"] = [(93, 50)]
    return dict


def getPassInfo(data):
    num = 0
    pos_ls = []
    pos_name_ls = []
    for ls in data:
        if ls[1] == "Huskies" and ls[6] == "Pass" and ls[3] != "":
            pos_ls.append(((eval(ls[8]), eval(ls[9])),
                           (eval(ls[10]), eval(ls[11]))))
    for j in pos_ls:
        if j[0] not in pos_name_ls:
            pos_name_ls.append(j[0])
        if j[1] not in pos_name_ls:
            pos_name_ls.append(j[1])

    pos_dict = getEmptyMatrix(pos_name_ls)
    # print(pos_ls)

    for j in pos_ls:
        pos_dict[j[0]][j[1]] += 1
        pos_dict[j[1]][j[0]] += 1

    # print(pos_dict)

    return pos_name_ls, pos_dict


def showPlot(name_list, data, edge_dict, pgr):
    dict = getPos(name_list, data)
    mean_x_ls = []
    mean_y_ls = []
    pos_ls = []
    color_ls = []
    size_ls = []
    id_dict = {}
    name2id = {}
    str2color = {"G": "#238E23", "F": "#BC1717", "M": "#D9D919", "D": "#3232CD"}
    id = -1

    # pgr = pagerank(edge_dict, name_list)

    for member in dict:
        # print(member, id)
        id += 1

        if member[8] == 'G':
            for i in range(dict[member].__len__()):
                if dict[member][i][0] == 0 and dict[member][i][1] == 0:
                    dict[member][i] = (7, 50)
                if dict[member][i][0] == 100 and dict[member][i][1] == 100:
                    dict[member][i] = (7, 50)

        x_ls = []
        y_ls = []
        for i in dict[member]:
            x_ls.append(i[0])
            y_ls.append(i[1])

        mean_x_ls.append(np.mean(x_ls))
        mean_y_ls.append(np.mean(y_ls))

        name2id[member] = id
        id_dict[id] = member[8:]
        pos_ls.append((np.mean(x_ls), np.mean(y_ls)))
        color_ls.append(str2color[member[8]])
        size_ls.append(pgr[member] * 300)

        # print(member, np.mean(x_ls), np.mean(y_ls))

    plt.xlim(0, 100)
    plt.ylim(0, 100)

    G = nx.Graph()

    for i in edge_dict:
        for j in edge_dict[i]:
            if i in name2id and j in name2id:
                G.add_edge(name2id[i], name2id[j], weight=edge_dict[i][j])

    nx.draw_networkx_edges(G, pos_ls, width=[float(d['weight'] / 10) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, pos_ls, node_color=color_ls, node_size=size_ls)
    nx.draw_networkx_labels(G, pos_ls, id_dict)

    plt.gca().invert_yaxis()
    plt.show()


def showAttackPlot(pos_list, pos_dict):
    G = nx.Graph()
    # print(pos_dict)
    for i in range(pos_list.__len__()):
        for j in range(pos_list.__len__()):
            G.add_edge(i, j, weight=pos_dict[pos_list[i]][pos_list[j]])

    nx.draw_networkx_edges(G, pos_list, width=[float(d['weight'] * 1) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, pos_list)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()
    plt.show()


def getZone(pos):
    if pos[0] <= 30:
        if pos[1] >= 75:
            return 'LWF'
        elif pos[1] >= 50:
            return 'LMF'
        elif pos[1] >= 25:
            return 'LCB'
        else:
            return 'LB'
    elif pos[0] >= 70:
        if pos[1] >= 75:
            return 'RWF'
        elif pos[1] >= 50:
            return 'RMF'
        elif pos[1] >= 25:
            return 'RCB'
        else:
            return 'RB'
    else:
        if pos[1] >= 85.7:
            return 'CF'
        elif pos[1] >= 71.4:
            return 'SS'
        elif pos[1] >= 57.1:
            return 'CAM'
        elif pos[1] >= 42.9:
            return 'CMF'
        elif pos[1] >= 28.6:
            return 'CB'
        else:
            return 'GK'


def getZone2(pos):
    if pos[0] == 100:
        pos = (99, pos[1])
    if pos[1] == 100:
        pos = (pos[0], 99)
    return int(pos[1] / 33.3) * 6 + int(pos[0] / 16.7)


def showZonePlot(pos_list, pos_dict):
    zone_name_ls = ['LWF', 'LMF', 'LCB', 'LB',
                    'RWF', 'RMF', 'RCB', 'RB',
                    'CF', 'SS', 'CAM', 'CMF', 'CDM', 'CB', 'GK']
    zone_pos_ls = [(87.5, 15), (62.5, 15), (37.5, 15), (12.5, 15),
                   (87.5, 85), (62.5, 85), (37.5, 85), (12.5, 85),
                   (92.9, 50), (78.6, 50), (64.3, 50), (50.0, 50), (35.7, 50), (21.4, 50), (7.14, 50)]
    G = nx.Graph()
    # print(pos_dict)

    zone_dict = getEmptyMatrix(zone_name_ls)

    for i in pos_list:
        for j in pos_list:
            zone_dict[getZone(i)][getZone(j)] += pos_dict[i][j]

    for i in range(zone_name_ls.__len__()):
        for j in range(zone_name_ls.__len__()):
            G.add_edge(i, j, weight=zone_dict[zone_name_ls[i]][zone_name_ls[j]])

    nx.draw_networkx_edges(G, zone_pos_ls, width=[float(d['weight'] / 10) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, zone_pos_ls)
    # nx.draw_networkx_labels(G, zone_pos_ls, id_dict)

    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()
    plt.show()


def showZone2Plot(pos_list, pos_dict):
    zone_pos_ls = []
    zone_name_ls = range(18)

    for i in range(3):
        for j in range(6):
            zone_pos_ls.append((100/12 + 100*j/6, 100/6 + 100*i/3))

    G = nx.Graph()
    # print(zone_pos_ls)

    zone_dict = getEmptyMatrix(zone_name_ls)

    for i in pos_list:
        for j in pos_list:
            zone_dict[getZone2(i)][getZone2(j)] += pos_dict[i][j]

    for i in range(zone_name_ls.__len__()):
        for j in range(zone_name_ls.__len__()):
            G.add_edge(i, j, weight=zone_dict[zone_name_ls[i]][zone_name_ls[j]])

    nx.draw_networkx_edges(G, zone_pos_ls, width=[float(d['weight'] / 10) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, zone_pos_ls)
    # nx.draw_networkx_labels(G, zone_pos_ls, id_dict)

    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()
    plt.show()


def showZone2Plot(zone_dict):
    zone_pos_ls = []

    for i in range(3):
        for j in range(6):
            zone_pos_ls.append((100/12 + 100*j/6, 100/6 + 100*i/3))

    G = nx.Graph()

    for i in range(18):
        for j in range(18):
            G.add_edge(i, j, weight=zone_dict[i][j])

    nx.draw_networkx_edges(G, zone_pos_ls, width=[float(d['weight'] / 10) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, zone_pos_ls)
    # nx.draw_networkx_labels(G, zone_pos_ls, id_dict)

    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()
    plt.show()


def pagerank(net, name_list):
    sum = {}
    dict = {}
    update = {}
    for i in name_list:
        dict[i] = 1
        sum[i] = 0
        update[i] = 0
    for i in name_list:
        for j in name_list:
            sum[i] += net[i][j]
    for epoch in range(10000):
        loss = 0
        for i in name_list:
            update[i] = 0
            for j in name_list:
                if sum[j] != 0:
                    update[i] += dict[j] * net[i][j] / sum[j]
        for i in name_list:
            loss += abs(update[i] - dict[i])
            dict[i] = update[i]
        if loss < 0.000001:
            # print(epoch)
            break
    return dict


def getEffectiveAttack(name_list, data):
    num = 0
    endnum = 0
    name_list.append("Huskies_Gate")
    dict = getEmptyMatrix(name_list)
    pos_ls = []
    pos_name_ls = []

    while endnum < data.__len__() and num < data.__len__():
        pass_num = 0
        duel_num = 0
        tmp_ls = []
        player_ls = []

        if data[num][6] != "Free Kick" and data[num][6] != "Pass":
            num += 1
            endnum += 1
            continue

        if data[num][1] != "Huskies":
            num += 1
            endnum += 1
            continue

        while endnum < data.__len__():

            if (data[endnum][6] == "Free Kick" or
                data[endnum][7] == "Acceleration" or
                data[endnum][7] == "Touch") and data[endnum][1] == "Huskies" and duel_num < 3:

                if data[endnum][3] != "":
                    player_ls.append((data[endnum][2], data[endnum][3]))
                    tmp_ls.append(((eval(data[endnum][8]), eval(data[endnum][9])),
                                   (eval(data[endnum][10]), eval(data[endnum][11]))))

                endnum += 1
                duel_num = 0

            elif data[endnum][6] == "Pass" and data[endnum][1] == "Huskies" and duel_num < 3:

                if data[endnum][3] != "":
                    pass_num += 1
                    tmp_ls.append(((eval(data[endnum][8]), eval(data[endnum][9])),
                                   (eval(data[endnum][10]), eval(data[endnum][11]))))
                    player_ls.append((data[endnum][2], data[endnum][3]))

                endnum += 1
                # print(endnum)
                duel_num = 0

            elif data[endnum][6] == "Duel" and duel_num < 3 and data[endnum][1] == "Huskies":
                endnum += 1
                duel_num += 1
            elif pass_num < 2 or data[endnum][6] != "Shot":
                num = endnum
                break
            else:
                player_ls.append((data[endnum][2], "Huskies_Gate"))

                for j in player_ls:
                    dict[j[0]][j[1]] += 10
                    dict[j[1]][j[0]] += 10
                    # if j[1] == "Huskies_Gate":
                    # print(j[0] + "!")

                tmp_ls.append(((eval(data[endnum][8]), eval(data[endnum][9])),
                               (93, 50)))
                # print("({0}, {1}) {2}".format(num + 2, endnum + 1, tmp_ls))
                pos_ls += tmp_ls
                num = endnum
                break

    for j in pos_ls:
        if j[0] not in pos_name_ls:
            pos_name_ls.append(j[0])
        if j[1] not in pos_name_ls:
            pos_name_ls.append(j[1])

    pos_dict = getEmptyMatrix(pos_name_ls)
    # print(pos_ls)

    for j in pos_ls:
        pos_dict[j[0]][j[1]] += 1
        pos_dict[j[1]][j[0]] += 1

    # showPlot(name_list, data, dict, pagerank(dict, name_list))
    # showAttackPlot(pos_name_ls, pos_dict)
    # showZonePlot(pos_name_ls, pos_dict)
    name_list.remove("Huskies_Gate")

    return dict, pos_ls


def getAverageByTime(data):
    pos_ls = []
    for time in range(5, 95, 5):
        print(time)
        x_ls = []
        y_ls = []
        for i in data:
            if i[4] == '1H':
                half = 0
            else:
                half = 45
            if eval(i[5]) / 60 + half < time - 5:
                continue
            if eval(i[5]) / 60 + half > time + half:
                break
            if i[1] == "Huskies":
                if i[8]:
                    x_ls.append(eval(i[8]))
                    y_ls.append(eval(i[9]))
        pos_ls.append((np.mean(x_ls), np.mean(y_ls)))
        # print(time, np.mean(x_ls), np.mean(y_ls))

    id_dict = {}

    for i in range(5, 95, 5):
        id_dict[int(i/5-1)] = i

    G = nx.Graph()
    for i in range(17):
        G.add_edge(i, i+1, weight=1)
    nx.draw_networkx_edges(G, pos_ls, width=[float(d['weight']) for (u, v, d) in G.edges(data=True)])
    nx.draw_networkx_nodes(G, pos_ls, node_size=200)
    nx.draw_networkx_labels(G, pos_ls, id_dict)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.gca().invert_yaxis()
    plt.show()


# full_data = read()
# full_name_list = getNameList(full_data)
# relation_dict = getEmptyMatrix(full_name_list)
# full_eva = getEmptyMatrix(full_name_list)
# full_zone = getEmptyMatrix(range(18))
# full_attack_zone = getEmptyMatrix(range(18))
# full_pgr = {}
# var_ls = []
# attack_var_ls = []

# for i in range(1, 39):
#     match_data = getMatchData(i, full_data)

#     name_list = getNameList(match_data)
#     time_range_dict = getTimeRangeDict(name_list, match_data)
#     pass_ls, pass_dic = getPassInfo(match_data)
#     attack_dic, attack_ls = getEffectiveAttack(name_list, match_data)
#     tmp_zone = getEmptyMatrix(range(18))
#     tmp_attack_zone = getEmptyMatrix(range(18))
#     degree_ls = []

#     for i in pass_ls:
#         for j in pass_ls:
#             full_zone[getZone2(i)][getZone2(j)] += pass_dic[i][j]
#             tmp_zone[getZone2(i)][getZone2(j)] += pass_dic[i][j]

#     for i in attack_ls:
#         full_attack_zone[getZone2(i[0])][getZone2(i[1])] += 1
#         full_attack_zone[getZone2(i[1])][getZone2(i[0])] += 1
#         tmp_attack_zone[getZone2(i[0])][getZone2(i[1])] += 1
#         tmp_attack_zone[getZone2(i[1])][getZone2(i[0])] += 1

#     for i in range(18):
#         sum = 0
#         for j in range(18):
#             if i != j:
#                 sum += tmp_zone[i][j]
#         degree_ls.append(sum)

#     var_ls.append(np.var(degree_ls))
#     degree_ls = []

#     for i in range(18):
#         sum = 0
#         for j in range(18):
#             if i != j:
#                 sum += tmp_attack_zone[i][j]
#         degree_ls.append(sum)

#     print(degree_ls)
#     attack_var_ls.append(np.var(degree_ls))

    # print(time_range_dict)

    # test start

    # if i == 14:
        # getEffectiveAttack(name_list, match_data)
        # tmpls, tmpdic = getPassInfo(match_data)
        # showZone2Plot(tmpls, tmpdic)
        # getAverageByTime(match_data)

    # test end

    # for j in name_list:
    #     for k in name_list:
    #         relation_dict[j][k] += 1

    # stab = stability(name_list, match_data)
    # acu = accuracy(name_list, match_data)
    # dif = difficulty(name_list, match_data)
    # time_dict = personReward(time_range_dict)

    # ws, wa, wd, stab, acu, dif = getWeight(stab, acu, dif, name_list)
    # eva = evaluation(name_list, stab, acu, dif, ws, wa, wd, time_dict)

    # for j in name_list:
    #     for k in name_list:
    #         full_eva[j][k] += eva[j][k]

    # pgr = pagerank(eva, name_list)

    # for j in name_list:
    #     if j in full_pgr:
    #         full_pgr[j] += pgr[j]
    #     else:
    #         full_pgr[j] = pgr[j]



    '''
    if i == 1:
        pass_dict = {}
        for j in name_list:
            pass_dict[j] = 0
        for j in match_data:
            if j[6] == "Pass" and j[1] == "Huskies":
                pass_dict[j[2]] += 1
        pass_ls = sorted(pass_dict.items(), key=lambda x:x[1], reverse=True)
        for i in pass_ls:
            print("{0}\t{1}".format(i[0], i[1]))
        pgr_ls = sorted(pgr.items(), reverse=True, key=lambda x: x[1])
        for i in pgr_ls:
            print("{0}\t{1}".format(i[0], i[1]))
    '''

    # print(pgr)
    # showPlot(name_list, match_data, eva, pgr)

# for i in full_name_list:
#     for j in full_name_list:
#         if relation_dict[i][j] == 0:
#             full_eva[i][j] = 0
#         else:
#             full_eva[i][j] /= relation_dict[i][j]

# for i in full_name_list:
#     full_pgr[i] /= relation_dict[i][i]

# showPlot(full_name_list, full_data, full_eva, full_pgr)

# full_attack_zone_ls = []

# for i in range(18):
#     full_attack_zone_ls.append([])
#     for j in range(18):
#         if i == j:
#             full_attack_zone_ls[i].append(0)
#         elif full_attack_zone[i][j] == 0:
#             full_attack_zone_ls[i].append(float('inf'))
#         else:
#             full_attack_zone_ls[i].append(1 / pow(full_attack_zone[i][j], 1))

# dis, edges = dijkstra(full_attack_zone_ls, 6)



# showZone2Plot(full_attack_zone)

# single_ls = []
# double_ls = []
# triple_ls = []

# for i in full_name_list:
#     for j in full_name_list:
#         if i == j:
#             break
#         double_ls.append((i, j, full_eva[i][j]))

# for i in full_name_list:
#     for j in full_name_list:
#         if i == j:
#             break
#         for k in full_name_list:
#             if j == k:
#                 break
#             triple_ls.append((i, j, k, full_eva[i][j] + full_eva[j][k] + full_eva[k][i]))

# single_ls = sorted(full_pgr.items(), reverse=True, key=lambda x: x[1])
# double_ls = sorted(double_ls, reverse=True, key=lambda x: x[2])
# triple_ls = sorted(triple_ls, reverse=True, key=lambda x: x[3])

# for i in range(10):
#     print("[#{0}]\t{1}\t{2}\t{3}\t{4}".format(i+1, triple_ls[i][0][8:], triple_ls[i][1][8:],
#                                               triple_ls[i][2][8:], triple_ls[i][3]))

# for i in range(10):
#     print("[#{0}]\t{1}\t{2}".format(i + 1, single_ls[i][0], single_ls[i][1]))
