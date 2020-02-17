import process

def get_attack_pattern(name_list, data):
    cur = 0
    op = []
    while cur < data.__len__():
        if data[cur][6] == "Shot":
            print("Found a shot at # " + str(cur))
            op.append('Shot')
            recurseId = cur - 1
            duelCnt = 0
            while recurseId >= 0:
                if data[recurseId][6] == "Duel":
                    duelCnt += 1
                    if duelCnt == 3:
                        op = []
                        break
                elif data[recurseId][6] == "Pass" and data[recurseId][1] == "Huskies":
                    op.append(data[recurseId][7])
                elif data[recurseId][1] == "Opponent":
                    op = []
                    break
                recurseId -= 1
            if len(op) > 0:
                print(op)

full_data = process.read()
match_data = process.getMatchData(1, full_data)
name_list = process.getNameList(match_data)
time_range_dict = process.getTimeRangeDict(name_list, match_data)

get_attack_pattern(name_list, match_data)