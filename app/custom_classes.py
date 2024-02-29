from jira import JIRA
import requests
from requests.auth import HTTPBasicAuth
import json


class SubTask:
    ''' Custom Sub-task class to be used in the process. '''
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Sub-task'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Story:
    ''' Custom Story class to be used in the process. '''
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Story'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Feature:
    ''' Custom Feature class to be used in the process. '''
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Feature'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Epic:
    ''' Custom Epic class to be used in the process. '''
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Epic'}
        for key, value in kwargs.items():
            setattr(self, key, value)

class Initiative:
    ''' Custom Initiative class (tailor-made for us) to be used in the process. '''
    def __init__(self, **kwargs):
        self.issuetype = {'name': 'Initiatief (SAFe Epic)'} # this is a custom type with hierarchy level 2 to be used as 'project' within the Jira project / workspace
        for key, value in kwargs.items():
            setattr(self, key, value)


class TeamMember:
    def __init__(self, name, account_id):
        self.name = name
        self.account_id = account_id

class JiraProcess:
    def __init__(self, domain, username, api_token, project_key, project_input, custom_fields: list = ['MOSS+ Directie', 'Story Points', 'MOSS+ Rol', 'Checklist Text']):
        self.jira_url = f'https://{domain}.atlassian.net'
        self.jira = JIRA(options={'server': self.jira_url}, basic_auth=(username, api_token))
        self.project_key = project_key
        self.project = self.jira.project(project_key)
        self.project_input = project_input
        self.users = self.get_users()
        self.users_by_name = self.get_users_by_name()
        self.issues = []
        self.custom_fields = self.get_custom_fields(custom_fields)
        self.directie_field = self.custom_fields['MOSS+ Directie']
        self.story_points_field = self.custom_fields['Story Points']
        self.rol_field = self.custom_fields['MOSS+ Rol']
        self.checklist_text_field = self.custom_fields['Checklist Text']
        # find all created labels (not yet in jira package)
        self.auth = HTTPBasicAuth(username, api_token)
        self.labels = self.make_regular_api_call('/rest/api/3/label').get('values', [])

    def get_custom_fields(self, field_names: list = []):
        ''' Gets all custom fields in the Jira project needed for this specific use case. '''
        custom_fields = {}

        for field in self.jira.fields():
            if field['name'] in field_names:
                custom_fields[field['name']] = field['id']
        return custom_fields

    def make_regular_api_call(self, endpoint):
        ''' Makes a regular API call to Jira. '''
        response = requests.get(f'{self.jira_url}{endpoint}', auth=self.auth)
        return response.json()

    def get_users(self):
        ''' Returns a list of all 'active' users in the Jira project.

        Returns:
            list[jira.User]: list of jira.User objects
        '''
        inactive_users = [
            'Bastiaan',
            'Cees',
            'Claire',
            'Cloud',
            'Dave',
            'Edwin',
            'Hugo',
            'Kübra',
            'Marcel',
            'Michael',
            'Nenad',
            'Paul',
            'Rob',
            'Ron',
            'Stefan'
        ]
        users = [user for user in self.jira.search_assignable_users_for_projects('', self.project_key) if user.displayName.split(' ')[0] not in inactive_users]
        
        # add all first names as attribute to user object
        for user in users:
            user.first_name = user.displayName.split(' ')[0]
        
        return users

    def get_users_by_name(self):
        return {user.displayName.split(' ')[0]: TeamMember(user.displayName, user.accountId) for user in self.users}


    def delete_all_issues(self):
        ''' Deletes all issues that have been created in the process. 
        
        Returns:
            list: list of deleted issue keys
        '''
        deleted_issue_keys = []

        # delete issues in reversed order because of parent-child hierarchy
        for issue in reversed(self.issues):
            try:
                issue.delete(deleteSubtasks=True)
                print(f'Deleted issue {issue.key}')
            except:
                print(f'Could not delete issue {issue.key}')
            deleted_issue_keys.append(issue.key)
        return deleted_issue_keys

    def prepare_issue_for_creation(self, issue):
        ''' Creating the issue needs a couple of fields to be modified. This function creates a dictionary with the correct fields.

        Args:
            issue (Issue): custom Epic, Feature or Story object with all the necessary fields
        '''
        issue_dict = {
            'project': {'key': self.project_key},
            'issuetype': issue.issuetype,
            'summary': issue.summary,
            'description': issue.description,
            'assignee': {'accountId': self.users_by_name[issue.assignee].account_id},
            'labels': [issue.label] if issue.label else [],
            self.directie_field: {'value': issue.directie}, # mandatory field
            self.rol_field: {'value': issue.role} # not manadatory in project, but will always be filled in this process
        }
        if hasattr(issue, 'parent'):
            issue_dict['parent'] = {'key': issue.parent}

            # let op, hiervoor moeten de issues in de 'appropriate hierarchy' staan in Jira
            # dat is niet altijd het geval omdat Jira niet is gemaakt voor SAFe, waarin stories onder features hangen (hiervoor hebben we Initiatief (SAFe Epic) gemaakt met hierarchy level 2)
            parent_hierarchy_level = self.jira.issue(issue.parent).fields.issuetype.hierarchyLevel
            current_issue_type = issue.issuetype['name']
            current_hierarchy_level = [issue_type.hierarchyLevel for issue_type in self.jira.issue_types() if issue_type.name == current_issue_type][0]
            if parent_hierarchy_level > current_hierarchy_level:
                issue_dict['parent'] = {'key': issue.parent}

            # of zo via relates, maar liever niet
            #     self.jira.create_issue_link('Relates', story.key, feature.key)


        if hasattr(issue, 'story_points'):
            issue_dict[self.story_points_field] = issue.story_points

        # currently for definition of done in epic
        if hasattr(issue, 'checklist_text'):
            issue_dict[self.checklist_text_field] = issue.checklist_text
        return issue_dict

    def create_issue(self, issue):
        ''' Creates an issue in Jira based on the issue dictionary.
        
        Args:
            issue (dict): dictionary with all the necessary fields
        '''
        issue_dict = self.prepare_issue_for_creation(issue)
        issue = self.jira.create_issue(fields=issue_dict)
        self.issues.append(issue)
        return issue
