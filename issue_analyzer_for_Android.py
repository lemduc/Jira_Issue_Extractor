import pickle
import pandas as pd

bug_file_mapping = pickle.load(open('output/bug_file_mapping_6_7.p', 'rb'))
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

print('total: ' + str(total_issue))
print('smelly: ' + str(smelly_issue))


print('total java: ' + str(total_java))
print('total non java: ' + str(total_non_java))
print('smelly java: ' + str(total_smelly_java))

