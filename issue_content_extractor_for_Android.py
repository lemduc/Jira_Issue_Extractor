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
            content = ""
            for l in output_split:
                if 'M\\t' in l:
                    continue
                if 'A\\t' in l:
                    continue
                if 'D\\t' in l:
                    continue
                if 'b"commit' in l:
                    continue
                if 'b\'commit' in l:
                    continue
                if 'Author:' in l:
                    continue
                if 'Date:' in l:
                    continue
                if 'Change-Id:' in l:
                    continue
                if 'bug:' in l.lower() or 'fixes:' in l.lower():
                    continue
                if l == "":
                    continue
                content += l + '\n';

            if bug_id in mapping_bug_description.keys():
                content += mapping_bug_description[bug_id]
            mapping_bug_description[bug_id] = content
    #else:  # merge commit
        #for parent in commit['parents']:
            #print(parent)
            #analyze_commit(parent['sha'])



with open('data/compare_7_8_local.txt', encoding="utf8") as data_file:
    data = data_file.readlines()

print(len(data))
mapping_bug_description = dict()

current_dir = os.getcwd()
os.chdir('C:\platform_frameworks_base')
command = 'git log --name-status --diff-filter="ACDMRT" -1 -U '

for commit in data[:]:
    commit_id = commit.split(' ', 1)[0]
    commit_message = commit.split(' ', 1)[1]
    analyze_commit(commit_id, commit_message)

#print(mapping_bug_file)
os.chdir(current_dir)

for key in mapping_bug_description:
    with open("issue_content/"+key+".txt", "w") as f:
        f.write(mapping_bug_description[key])
