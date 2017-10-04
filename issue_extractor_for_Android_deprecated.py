import requests
import time
import json
import re
import subprocess
import os

#from requests.auth import HTTPBasicAuth
#r = requests.get('https://api.github.com/user', auth=HTTPBasicAuth('lemduc', 'meocon2012'))
#r = requests.get('https://api.github.com/repos/android/platform_frameworks_base')
#r = requests.get('https://api.github.com/repos/android/platform_frameworks_base/commits?sha=oreo-dev&since=2017-01-01T00:00:00Z')
#if (r.ok):
#    repoItem = json.loads(r.text or r.content)
#    print("Framework repository created: " + repoItem['created_at'])

def analyze_commit(sha):
    output = subprocess.check_output(command + sha)
    #content = json.loads(r.text)
    if 'Merge' not in str(output):  # normal commit
        # print(commit['commit']['message'])
        bug_id = ""
        for line in str(output).split('\\n'):
            if 'bug:' in line.lower() or 'fixes:' in line.lower():
                # print(line)
                bug_id = re.findall(r"\d{8}", line)[0]
                print(bug_id)  # re.findall(r"\D(\d{5})\D", " "+s+" ")
                file_list = list()
                for l in str(output).split('\\n'):
                    if 'M\\t' in l:
                        file_path = l.replace('M\\t', '')
                        file_list.append(file_path)
                        print(file_path)
                    if 'A\\t' in l:
                        file_path = l.replace('A\\t', '')
                        file_list.append(file_path)
                        print(file_path)
                    if 'D\\t' in l:
                        file_path = l.replace('D\\t', '')
                        file_list.append(file_path)
                        print(file_path)
        if bug_id != "":
            if bug_id in mapping_bug_file.keys():
                file_list.extend(mapping_bug_file[bug_id])
            mapping_bug_file[bug_id] = file_list
    #else:  # merge commit
        #for parent in commit['parents']:
            #print(parent)
            #analyze_commit(parent['sha'])



with open('data/7_0_0_r1_vs_8_0_0_r1.txt') as data_file:
    data = json.load(data_file)

print(len(data['commits']))
mapping_bug_file = dict()

os.chdir('C:\platform_frameworks_base')
command = 'git log --name-status --diff-filter="ACDMRT" -1 -U '

for commit in data['commits']:
    #print(commit['commit']['message'])
    #time.sleep(1)
    if 'Merge' not in commit['commit']['message']: #normal commit
        #print(commit['commit']['message'])
        for line in commit['commit']['message'].split('\n'):
            if 'bug:' in line.lower() or 'fixes:' in line.lower():
                #print(line)
                bug_id = re.findall(r"\d{8}", line)[0]
                print(bug_id) #re.findall(r"\D(\d{5})\D", " "+s+" ")
                output = subprocess.check_output(command + commit['sha'])
                print()
                #subprocess.call(command + commit['sha'])
                #print(re.findall(r"M\\t{.}*$", str(output)))
                file_list = list()
                if bug_id in mapping_bug_file.keys():
                    file_list = mapping_bug_file[bug_id]
                for l in str(output).split('\\n'):
                    if 'M\\t' in l:
                        file_path = l.replace('M\\t', '')
                        file_list.append(file_path)
                        print(file_path)
                    if 'A\\t' in l:
                        file_path = l.replace('A\\t', '')
                        file_list.append(file_path)
                        print(file_path)
                    if 'D\\t' in l:
                        file_path = l.replace('D\\t', '')
                        file_list.append(file_path)
                        print(file_path)
                mapping_bug_file[bug_id] = file_list
                #exit()
        # r = requests.get('https://api.github.com/repos/android/platform_frameworks_base/commits/' + commit['sha'])
        # content = json.loads(r.text)
        # files = content['files']
        # for file in files:
        #     print (file['filename'])
        #print(r)
    else: #merge commit
        #for parent in commit['parents']:
            #print(parent['sha'])
            #analyze_commit(parent['sha'])
        analyze_commit(commit['sha'])


print(mapping_bug_file)