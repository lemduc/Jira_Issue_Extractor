import pickle
import pandas as pd

bug_file_mapping = pickle.load(open('output/bug_file_mapping_7_8.p', 'rb'))
print((len(bug_file_mapping)))

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

file = r'data/arc_comp.xls'
df = pd.read_excel(file)

buo_set = set()
bdc_set = set()
spf_set = set()
bco_set = set()
has_smell_set = set()

for line in df.as_matrix():
    filename = convertClassName(line[0])
    if line[1] == 1:
        buo_set.add(filename)
        has_smell_set.add(filename)
    if line[2] == 1:
        bdc_set.add(filename)
        has_smell_set.add(filename)
    if line[3] == 1:
        spf_set.add(filename)
        has_smell_set.add(filename)
    if line[4] == 1:
        bco_set.add(filename)
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
        if convertAndroidClassName(file) in has_smell_set:
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

write_out = "bug id, has_smell \n"

for key in bug_file_mapping:
    if key in smell_issue_set:
        write_out += key + ", true \n"
    else:
        write_out += key + ", false \n"


with open('output/predict_has_smell_7_8_arc_all.csv', 'w', encoding="utf8") as data_file:
    data_file.write(write_out)
