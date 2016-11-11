import time
import json
import datetime
import requests

from urllib.request import urlopen
import re
from datetime import datetime, date
from collections import OrderedDict
from jira import JIRA

options = {
    'server': 'https://issues.apache.org/jira/'
}

project_name = "Nutch"


###########################################################
# Find the list of isues #

jira = JIRA(options)
sess_get = jira._session.get
projects = jira.projects()

for p in projects:
    # print(p.name)
    if p.name == project_name:
        project = p
        print(project.name)
        break

issues = []

keepCrawling = True
i = 5
while keepCrawling:
    tmp = jira.search_issues('project=' + project.key + ' AND status in (Resolved, Closed) AND resolution=Fixed',
                             startAt=i, maxResults=100)
    print('.', end="")
    if (len(tmp) > 0):
        issues.extend(tmp)
        i = i + 100
        #keepCrawling = False #temple limitation
    else:
        keepCrawling = False

# Jira on Apache has a limitation of 100
print('Total number of issues: ' + str(len(issues)))

###########################################################
# Download isues #

storeIssues = []

timeFormat = "%Y-%m-%dT%H:%M:%S.000+0000"

for issue in issues:
    try:
        print('.', end="")
        exportedData = OrderedDict([])

        try:
            affectversion = {'affect': issue.fields.versions[0].name}
        except Exception:
            affectversion = {'affect': ""}

        # print(issue.fields.versions)
        try:
            output = ""
            for s in issue.fields.versions:
                output = output + s.name + ","
            # print(output)
            allaffectversion = {'all_affect': output[:-1]}
        except Exception:
            allaffectversion = {'all_affect': ""}

        try:
            fixversion = {'fix': issue.fields.fixVersions[0].name}
        except Exception:
            fixversion = {'fix': ""}

        try:
            output = ""
            for s in issue.fields.fixVersions:
                output = output + s.name + ","
            # print(output)
            allfixversion = {'all_fix': output[:-1]}
        except Exception:
            allfixversion = {'all_fix': ""}

        priority = {'priority': issue.fields.priority.name}
        resolvedDate = datetime.strptime(issue.fields.resolutiondate, timeFormat)
        createdDate = datetime.strptime(issue.fields.created, timeFormat)
        fixdays = {'time': (resolvedDate - createdDate).seconds}
        issue_type = {'type': issue.fields.issuetype.name}
        issue_id = {'issue_id': issue.key}

        # print(affectversion)
        # print(fixversion)
        # print(priority)
        # print(fixdays)
        exportedData.update(issue_id)
        exportedData.update(affectversion)
        exportedData.update(fixversion)
        exportedData.update(priority)
        exportedData.update(issue_type)
        exportedData.update(fixdays)
        exportedData.update(allaffectversion)
        exportedData.update(allfixversion)

        # DEV_STATUS = 'https://issues.apache.org/jira/rest/dev-status/1.0'
        # _issue = 'issue/detail?issueId=%s' % issue.id
        # _args = 'applicationType=fecru&dataType=repository&_=%s' % int(time.time())
        # req_url = '%s/%s&%s' % (DEV_STATUS, _issue, _args)
        # response = sess_get(req_url)
        # raw_data = json.loads(response.content.decode('utf-8'))
        # # print(issue)
        # # print(issue.key)
        # # print(raw_data)
        # try:
        #     hasCommit = True
        #     commits = raw_data['detail'][0]['repositories'][0]['commits']
        #     # storeIssues.append(response.content.decode('utf-8'))
        # except IndexError:
        #     hasCommit = False
        # if hasCommit:
        #     commitList = []
        #     for commit in commits:
        #         # print(req)
        #         # print(issue.id)
        #         patches = []
        #         # print('%s\n%s\n\n' % (req['displayId'], req['files']))
        #         for file in commit['files']:
        #             patches.append({'filename': file['path']})
        #         commitList.append({'files': patches})
        #         # print(patches)
        #     exportedData.update({'commits': commitList})
        #     storeIssues.append(exportedData)
        hasCommit = False
        # if doesn't has commit, then find by pull request
        if not hasCommit:
            DEV_STATUS = 'https://issues.apache.org/jira/secure/AjaxIssueAction!default.jspa?'
            _issue = 'issueKey=%s' % issue.id
            _args = '&_=%s' % int(time.time())
            #_args = 'applicationType=github&dataType=pullrequest&_=%s' % int(time.time())
            req_url = '%s%s&%s' % (DEV_STATUS, _issue, _args)
            response = sess_get(req_url)
            raw_data = json.loads(response.content.decode('utf-8'))


            # find by regular expression
            pull_request = re.compile('https:\/\/github.com\/apache\/'+project_name.lower()+'\/pull\/[0-9]*')
            matched = pull_request.findall(raw_data['panels']['leftPanels'][2]['html'])
            if matched is not None and len(matched) != 0:
                pull_requests = set(matched);
                commitList = []
                for link in pull_requests:
                    githubLink = str(link).replace('https://github.com/', 'https://api.github.com/repos/').replace('pull', 'pulls')+'/files' + '?access_token=b1077655202a74c42d8ee5145c154b14a7db07e9';
                    print(githubLink)
                    related_files = requests.get(githubLink).json();
                    patches = []
                    for file in related_files:
                        print(file['filename'])
                        patches.append({'filename': file['filename']})
                    commitList.append({'files': patches})
                    # print(patches)
                exportedData.update({'commits': commitList})
                storeIssues.append(exportedData)
            else:
                hasPullRequest = False
                if not hasCommit and not hasPullRequest:
                    # try to look for patch file
                    # find by regular expression
                    patch_file = re.compile('https:\/\/issues.apache.org\/jira\/secure\/attachment\/[0-9]*\/[^.]+.patch')
                    matched = patch_file.findall(raw_data['panels']['leftPanels'][2]['html'])
                    java_file_pattern = re.compile('[^ ]+\.java');
                    if matched is not None:
                        commitList = []
                        for patch in set(matched):
                            patches = []
                            content = requests.get(patch).content
                            # print(content.read())
                            java_files = java_file_pattern.findall(str(content))
                            for f in set(java_files):
                                patches.append({'filename': f})
                            commitList.append({'files': patches})
                        exportedData.update({'commits': commitList})
                        storeIssues.append(exportedData)
            # Done with collecting



    except:
        print(issue)

with open(project_name + '_data.json', 'w') as outfile:
    json.dump(storeIssues, outfile)

    # print(issues)

    # issue = jira.issue('JRA-9')
    # print(issue.fields.project.key)             # 'JRA'
    # print(issue.fields.issuetype.name)          # 'New Feature'
    # print(issue.fields.reporter.displayName)  # 'Mike Cannon-Brookes [Atlassian]'