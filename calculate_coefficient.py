import process
import matplotlib.pyplot as plt

# mat is a dictionary containing edge gains between players
def calculateClusteringCoefficient(mat, name_list):
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

full_data = process.read()
full_name_list = process.getNameList(full_data)
relation_dict = process.getEmptyMatrix(full_name_list)
full_eva = process.getEmptyMatrix(full_name_list)
full_pgr = {}
print(full_eva.__sizeof__())
full_coef = []

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

    coef = calculateClusteringCoefficient(eva, name_list)
    coef_sum = 0
    for name in name_list:
        coef_sum += coef[name]
    full_coef.append(coef_sum - 7.5)

color = ['red', 'blue', 'green', 'green', 'green', 'red', 'green', 'blue', 'green', 
'green', 'red', 'blue', 'green', 'red', 'red', 'blue', 'red', 'red', 'blue', 'blue', 
'green', 'green', 'green', 'blue', 'red', 'green', 'red', 'green', 'green', 'red', 'red', 
'green', 'blue', 'blue', 'red', 'red', 'blue', 'green']
plt.bar(range(38), full_coef, color = color)
plt.show()
