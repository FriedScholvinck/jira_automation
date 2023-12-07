from jira import JIRA

class TeamMember:
    def __init__(self, name, account_id):
        self.name = name
        self.account_id = account_id

class JiraProcess:
    def __init__(self, domain, username, api_token, project_key, project_input):
        self.jira_url = f'https://{domain}.atlassian.net'
        self.jira = JIRA(options={'server': self.jira_url}, basic_auth=(username, api_token))
        self.project_key = project_key
        self.project = self.jira.project(project_key)
        self.project_input = project_input
        self.users = self.get_users()
        self.users_by_name = self.get_users_by_name()
        self.epic = None
        self.features = []
        self.stories = []
        self.directie_field = [field['id'] for field in self.jira.fields() if field['name'] == 'MOSS+ Directie'][0]
        self.story_points_field = [field['id'] for field in self.jira.fields() if field['name'] == 'Story Points'][0]
        self.rol_field = [field['id'] for field in self.jira.fields() if field['name'] == 'MOSS+ Rol'][0]

    def get_users(self):
        ''' Returns a list of all 'active' users in the Jira project.

        Returns:
            list[jira.User]: list of jira.User objectsa
        '''
        inactive_users = [
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
            list: list of deleted issues
        '''

        deleted_issues = self.features + self.stories + [self.epic] if self.epic else self.features + self.stories
        for issue in deleted_issues:
            issue.delete()
        return deleted_issues

    def create_epic(self):
        epic_title = f"[Epic {self.project_input['sub_project']}_{self.project_input['quarter']}] "
        epic_dict = {
            'project': {'key': self.project_key},
            'summary': epic_title + self.project_input['name'],
            'description': self.project_input['description'],
            'issuetype': {'name': 'Epic'},
            'assignee': {'accountId': self.users_by_name[self.project_input['roles']['Business Analist']].account_id},
            'labels': [self.project_input['sub_project']],
            self.directie_field: {'value': self.project_input['directie']},
            self.rol_field: {'value': 'Business Analist'}
        }
        self.epic = self.jira.create_issue(fields=epic_dict)
        return self.epic

    def create_feature(self, role, summary, assignee):
        feature_title = f"[Feature {self.project_input['sub_project']}_{self.project_input['quarter']}] "
        feature_dict = {
            'project': {'key': self.project_key},
            'summary': feature_title + summary,
            'description': self.project_input['description'],
            'issuetype': {'name': 'Feature'},
            'assignee': {'accountId': self.users_by_name[assignee].account_id},
            'labels': [self.project_input['sub_project']],
            self.directie_field: {'value': self.project_input['directie']},
            self.rol_field: {'value': role},
            'parent': {'key': self.epic.key}
        }
        feature = self.jira.create_issue(fields=feature_dict)
        self.features.append(feature)
        return feature

    def create_story(self, story_fields, feature):
        story_title = f"[Story {self.project_input['sub_project']}_{self.project_input['quarter']}] "
        story_dict = {
            'project': {'key': self.project_key},
            'summary': story_title + story_fields['summary'],
            'description': story_fields.get('description', '') + f"\n\nStory Points: {story_fields.get('story_points', '...')}",
            'issuetype': {'name': 'Story'},
            'assignee': {'accountId': feature.fields.assignee.accountId},
            'labels': [self.project_input['sub_project']],
            'parent': {'key': self.epic.key},
            self.directie_field: {'value': self.project_input['directie']},
            self.story_points_field: story_fields.get(self.story_points_field, 1),
            self.rol_field: {'value': story_fields.get('role', 'Business Analist')}
        }
        story = self.jira.create_issue(fields=story_dict)
        self.jira.create_issue_link('Relates', story.key, feature.key)
        self.stories.append(story)
        return story
