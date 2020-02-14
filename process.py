import re
import math
import numpy as np


def sigmoid(x):
     y = 1.0 / (1.0 + np.exp(-x))
     return y


# read csv file.
def read():
    with open("fullevents.csv", 'r') as f:
        full_ls = []
        for i in f.readlines()[1:1522]:
            ls = i[:-1].split(',')
            full_ls.append(ls)
            # print(ls)
    return full_ls


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


# get numbers of successful passes (2-dimension dictionary).
def getPassMatrix(name_list, data):
    dict = getEmptyMatrix(name_list)
    for i in data:
        if i[1] == "Huskies" and i[3] != "" and i[6] == "Pass":
            dict[i[2]][i[3]] += 1
            dict[i[3]][i[2]] += 1
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


# get edge gains of passing (2-dimension dictionary).
def passReward(name_list, data):
    num = 0
    endnum = 0
    dict = getEmptyMatrix(name_list)

    while endnum < 1521 and num < 1521:
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

        while endnum < 1521:
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
                endnum += 1
                if data[endnum][3] != "":
                    pass_num += 1
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
                    dict[players[0]][players[1]] += float(pow(max(mean - 30, 0), 2)) / 3000
                    dict[players[1]][players[0]] += float(pow(max(mean - 30, 0), 2)) / 3000
                    # print(float(pow(max(mean - 30, 0), 2)) / 3000)
                num = endnum
                break

    return dict


# get node gains of passing (dictionary).
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



full_data = read()
name_list = getNameList(full_data)
time_range_dict = getTimeRangeDict(name_list, full_data)

print(personPenalty2(name_list, full_data))
















