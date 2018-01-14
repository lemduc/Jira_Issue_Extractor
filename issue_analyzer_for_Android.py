import pickle
import pandas as pd
from scipy import stats
import numpy

bug_file_mapping = pickle.load(open('output/bug_file_mapping_7_8.p', 'rb'))
print((len(bug_file_mapping)))

#dict

def convertClassName(file_name):
    if '$' in file_name:
        return file_name.split('$')[0]

    else:
        return file_name

def convertAndroidClassName(file_name: str):
    if not file_name.endswith('java'):
        return None
    else:
        tmp_1 = file_name.replace(".java", "").replace("/", ".")
        if '.java.' in tmp_1:
            return tmp_1.split(".java.")[1]
        else:
            return tmp_1

file = r'data/acdc_comp.xls'
df = pd.read_excel(file)

buo_set = set()
bdc_set = set()
has_smell_set = set()

for line in df.as_matrix():
    filename = convertClassName(line[0])
    if line[1] == 1:
        buo_set.add(filename)
        has_smell_set.add(filename)
    if line[2] == 1:
        bdc_set.add(filename)
        has_smell_set.add(filename)

print('compute correlation')

total_issue = 0
smelly_issue = 0

total_java = 0
total_non_java = 0
total_smelly_java = 0

non_smell_issue_set = set()
smell_issue_set = set()

for key in bug_file_mapping.keys():
    has_smell = False
    file_list = bug_file_mapping[key]
    total_issue +=1
    for file in file_list:
        total_java +=1
        if convertAndroidClassName(file) in buo_set:
            total_smelly_java +=1
            has_smell = True
        if convertAndroidClassName(file) == None:
            total_non_java +=1

    if has_smell:
        smelly_issue += 1
        smell_issue_set.add(key)
    else:
        non_smell_issue_set.add(key)

count_file_smell = list()
count_file_non_smell = list()

for key in smell_issue_set:
    c = 0
    for file in bug_file_mapping[key]:
        if file.endswith('java'):
            c += 1
    count_file_smell.append(c)

for key in non_smell_issue_set:
    c = 0
    for file in bug_file_mapping[key]:
        if file.endswith('java'):
            c += 1
    count_file_non_smell.append(c)

st =  stats.ttest_ind(count_file_smell, count_file_non_smell)

count_issue_per_smelly_file = dict()
count_issue_per_non_smelly_file = dict()

commit_set_per_smelly_file = dict()
commit_set_per_non_smelly_file = dict()

for issue in smell_issue_set:
    for file in bug_file_mapping[issue]:
        if file not in count_issue_per_smelly_file.keys():
            count_issue_per_smelly_file[file] = 0
            commit_set_per_smelly_file[file] = set()
        count_issue_per_smelly_file[file] += 1
        commit_set_per_smelly_file[file].add(issue)

for issue in non_smell_issue_set:
    for file in bug_file_mapping[issue]:
        if file not in count_issue_per_non_smelly_file.keys():
            count_issue_per_non_smelly_file[file] = 0
            commit_set_per_non_smelly_file[file] = set()
        count_issue_per_non_smelly_file[file] += 1
        commit_set_per_non_smelly_file[file].add(issue)

s = list()
n = list()

for key in count_issue_per_smelly_file.keys():
    s.append(count_issue_per_smelly_file[key])

for key in count_issue_per_non_smelly_file.keys():
    n.append(count_issue_per_non_smelly_file[key])

st2 =  stats.ttest_ind(count_file_smell, count_file_non_smell)

print('total: ' + str(total_issue))
print('smelly: ' + str(smelly_issue))


print('total java: ' + str(total_java))
print('total non java: ' + str(total_non_java))
print('smelly java: ' + str(total_smelly_java))

print('Question 1:')
print('p-value:' + str(st))
print('mean smell:' + str(numpy.mean(count_file_smell)))
print('non mean smell:' + str(numpy.mean(count_file_non_smell)))

print('Question 2:')
print('p-value:' + str(st2))
print('mean smell:' + str(numpy.mean(s)))
print('non mean smell:' + str(numpy.mean(n)))


s = [(k, count_issue_per_smelly_file[k]) for k in sorted(count_issue_per_smelly_file, key=count_issue_per_smelly_file.get, reverse=True)]
ns = [(k, count_issue_per_non_smelly_file[k]) for k in sorted(count_issue_per_non_smelly_file, key=count_issue_per_non_smelly_file.get, reverse=True)]

count = 0
for file in s:
    if file[0].endswith('java'):
        count += 1
    else:
        continue
    if count > 10:
        break
    print(file)
    # for iss in commit_set_per_smelly_file[file[0]]:
    #     print (iss)

count = 0
for file in ns:
    if file[0].endswith('java'):
        count += 1
    else:
        continue
    if count > 10:
        break
    print(file)