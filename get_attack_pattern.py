import process
import matplotlib.pyplot as plt

attack_pattern = {}

def judge_attack_pattern(op):
    if "Free kick shot" in op or "Penalty" in op:
        if attack_pattern.__contains__('placekick'):
            attack_pattern['placekick'] += 1
        else:
            attack_pattern['placekick'] = 1
    elif op[1] == 'Cross' or op[2] == 'Cross':
        if attack_pattern.__contains__('cross'):
            attack_pattern['cross'] += 1
        else:
            attack_pattern['cross'] = 1
    elif "Launch" in op or "High pass" in op:
        if attack_pattern.__contains__('long pass'):
            attack_pattern['long pass'] += 1
        else:
            attack_pattern['long pass'] = 1
    else:
        if attack_pattern.__contains__('control'):
            attack_pattern['control'] += 1
        else:
            attack_pattern['control'] = 1

def get_attack_pattern(name_list, data):
    cur = 0
    op = []
    while cur < data.__len__():
        if data[cur][1] == "Huskies" and data[cur][6] == "Shot":
            # print(str(cur))
            op.append('Shot')
            recurseId = cur - 1
            duelCnt = 0
            passCnt = 0
            while recurseId >= 0:
                if data[recurseId][6] == "Duel":
                    duelCnt += 1
                    if duelCnt == 3:
                        break
                elif data[recurseId][1] == "Huskies" and (data[recurseId][6] == "Pass" or data[recurseId][7] == "Free kick cross"):
                    passCnt += 1
                    duelCnt = 0
                    op.append(data[recurseId][7])
                elif data[recurseId][1] == "Opponent":
                    break
                recurseId -= 1
            if len(op) > 0:
                if passCnt >= 3:
                    # print(op)
                    judge_attack_pattern(op)
                op = []
        elif data[cur][1] == "Huskies" and (data[cur][7] == "Free kick shot" or data[cur][7] == "Panalty"):
            op.append(data[cur][7])
            # print(op)
            judge_attack_pattern(op)
            op = []
        cur += 1

full_data = process.read()
diversity = []
for i in range(1, 39):
    attack_pattern = {}
    match_data = process.getMatchData(i, full_data)
    name_list = process.getNameList(match_data)
    time_range_dict = process.getTimeRangeDict(name_list, match_data)

    get_attack_pattern(name_list, match_data)
    diversity.append(len(attack_pattern))
plt.bar(range(1,39), diversity)
plt.show()