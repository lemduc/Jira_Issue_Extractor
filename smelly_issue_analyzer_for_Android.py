import pickle
import pandas as pd
from scipy import stats
import numpy
import os
import subprocess
import re

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


def analyze_commit(sha, commit_message):
    os.chdir('C:\platform_frameworks_base')
    output = str(subprocess.check_output(command + sha))
    output_split = output.split('\\n')
    # content = json.loads(r.text)
    if not commit_message.lower().startswith('merge'):  # normal commit
        # print(commit['commit']['message'])
        bug_id = ""
        for line in output_split:
            if 'bug:' in line.lower() or 'fixes:' in line.lower():
                print(line)
                bug_id_list = re.findall(r"\d{7,8}", line)
                if (len(bug_id_list) > 0):
                    bug_id = bug_id_list[0]
                    # print(bug_id)  # re.findall(r"\D(\d{5})\D", " "+s+" ")
                    break
        if bug_id != "" and bug_id in smell_issue_set:
            content = ""
            for l in output_split:
            #     if 'M\\t' in l:
            #         continue
            #     if 'A\\t' in l:
            #         continue
            #     if 'D\\t' in l:
            #         continue
                if 'b"commit' in l:
                    l = l.replace('b"', "")
                if 'b\'commit' in l:
                    l = l.replace('b\'', "")
            #     if 'Author:' in l:
            #         continue
            #     if 'Date:' in l:
            #         continue
            #     if 'Change-Id:' in l:
            #         continue
            #     if 'bug:' in l.lower() or 'fixes:' in l.lower():
            #         continue
            #     if l == "":
            #         continue
                content += l + '\n';
            os.chdir(current_dir)
            with open("smelly_issue_content/" + bug_id + ".txt", "a") as f:
                f.write(content)

with open('data/compare_6_7_local.txt', encoding="utf8") as data_file:
    data = data_file.readlines()

current_dir = os.getcwd()
command = 'git log --name-status --diff-filter="ACDMRT" -1 -U '

for commit in data[:]:
    commit_id = commit.split(' ', 1)[0]
    commit_message = commit.split(' ', 1)[1]
    analyze_commit(commit_id, commit_message)





