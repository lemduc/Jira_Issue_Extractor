import pickle
import re
import subprocess
import os

# Can implement to make this parallel and faster

def analyze_commit(sha, commit_message):
    output = str(subprocess.check_output(command + sha))
    output_split = output.split('\\n')
    #content = json.loads(r.text)
    if not commit_message.lower().startswith('merge'):  # normal commit
        # print(commit['commit']['message'])
        bug_id = ""
        for line in output_split:
            if 'bug:' in line.lower() or 'fixes:' in line.lower():
                print(line)
                bug_id_list = re.findall(r"\d{7,8}", line)
                if (len(bug_id_list)>0):
                    bug_id = bug_id_list[0]
                    #print(bug_id)  # re.findall(r"\D(\d{5})\D", " "+s+" ")
                    break
        if bug_id != "":
            file_list = list()
            for l in output_split:
                if 'M\\t' in l:
                    file_path = l.replace('M\\t', '')
                    file_list.append(file_path)
                    #print(file_path)
                if 'A\\t' in l:
                    file_path = l.replace('A\\t', '')
                    file_list.append(file_path)
                    #print(file_path)
                if 'D\\t' in l:
                    file_path = l.replace('D\\t', '')
                    file_list.append(file_path)
                    #print(file_path)

            if bug_id in mapping_bug_file.keys():
                file_list.extend(mapping_bug_file[bug_id])
            mapping_bug_file[bug_id] = file_list
    #else:  # merge commit
        #for parent in commit['parents']:
            #print(parent)
            #analyze_commit(parent['sha'])



with open('data/compare_6_7_local.txt', encoding="utf8") as data_file:
    data = data_file.readlines()

print(len(data))
mapping_bug_file = dict()

current_dir = os.getcwd()
os.chdir('C:\platform_frameworks_base')
command = 'git log --name-status --diff-filter="ACDMRT" -1 -U '

for commit in data[:]:
    commit_id = commit.split(' ', 1)[0]
    commit_message = commit.split(' ', 1)[1]
    analyze_commit(commit_id, commit_message)

#print(mapping_bug_file)
os.chdir(current_dir)
pickle.dump(mapping_bug_file, open("output/bug_file_mapping_6_7.p", "wb"))
