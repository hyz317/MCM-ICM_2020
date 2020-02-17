import process
import matplotlib.pyplot as plt

# mat is a dictionary containing edge gains between players
def clusteringCoefficientBarat(mat, name_list):
    coef = {}
    for name in name_list:
        tmp = 0.0
        s = 0
        for j in name_list:
            if j != name:
                s += 1
            for k in name_list:
                if j != k:
                    if mat[name].__contains__(j) and mat[name].__contains__(k):
                        tmp += (mat[name][j] + mat[name][k]) / 2
        coef[name] = tmp / (len(mat[name]) - 1) / s
    return coef

def clusteringCoefficientOnnela(mat, name_list):
    coef = {}
    for name in name_list:
        tmp = 0.0
        for j in name_list:
            if j != name:
                for k in name_list:
                    if k != name and k != j:
                        if mat[name].__contains__(j) and mat[j].__contains__(k) and mat[k].__contains__(name):
                            tmp += pow(mat[name][j] * mat[j][k] * mat[k][name], 1/3)
        a = len(mat[name])
        coef[name] = tmp / a / (a - 1)
    return coef


full_data = process.read()
full_name_list = process.getNameList(full_data)
relation_dict = process.getEmptyMatrix(full_name_list)
full_eva = process.getEmptyMatrix(full_name_list)
full_pgr = {}
print(full_eva.__sizeof__())
full_coef = {}
game_competed = {}

for i in range(1, 39):
    match_data = process.getMatchData(i, full_data)

    name_list = process.getNameList(match_data)
    time_range_dict = process.getTimeRangeDict(name_list, match_data)

    # print(time_range_dict)

    for j in name_list:
        for k in name_list:
            relation_dict[j][k] += 1

    stab = process.stability(name_list, match_data)
    acu = process.accuracy(name_list, match_data)
    dif = process.difficulty(name_list, match_data)
    time_dict = process.personReward(time_range_dict)

    ws, wa, wd, stab, acu, dif = process.getWeight(stab, acu, dif, name_list)
    eva = process.evaluation(name_list, stab, acu, dif, ws, wa, wd, time_dict)

    for j in name_list:
        for k in name_list:
            full_eva[j][k] += eva[j][k]

#     coef = clusteringCoefficientOnnela(eva, name_list)
#     coef_sum = 0
#     for name in name_list:
#         coef_sum += coef[name]
#     full_coef.append(coef_sum / len(name_list))

# color = ['red', 'blue', 'green', 'green', 'green', 'red', 'green', 'blue', 'green', 
# 'green', 'red', 'blue', 'green', 'red', 'red', 'blue', 'red', 'red', 'blue', 'blue', 
# 'green', 'green', 'green', 'blue', 'red', 'green', 'red', 'green', 'green', 'red', 'red', 
# 'green', 'blue', 'blue', 'red', 'red', 'blue', 'green']
# plt.bar(range(38), full_coef, color = color)
# plt.show()

    coef = clusteringCoefficientBarat(eva, name_list)
    for name in name_list:
        if full_coef.__contains__(name):
            full_coef[name] += coef[name]
        else:
            full_coef[name] = coef[name]
        if game_competed.__contains__(name):
            game_competed[name] += 1
        else:
            game_competed[name] = 1

print("----------")
print(game_competed)
print(full_coef)
idx = {}
for name in full_coef.keys():
    full_coef[name] = full_coef[name] / game_competed[name]
tmp = sorted(full_coef.items(), reverse = True, key=lambda d: d[1])
print("----------")
for i in range(30):
    print("[#{0}]\t{1}\t{2}".format(i+1, tmp[i][0], tmp[i][1]))