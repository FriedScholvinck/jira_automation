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
        self.project_input = project_input
        self.users = []
        self.team_members = self.get_team_members()
        self.epic = None
        self.features = []
        self.stories = []
        # self.validate_roles()

    def get_team_members(self):
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
            'Remko',
            'Rob',
            'Ron',
            'Stefan'
        ]
        self.users = [user for user in self.jira.search_assignable_users_for_projects('', self.project_key) if user.active and user.displayName.split(' ')[0] not in inactive_users]
        return {user.displayName.split(' ')[0]: TeamMember(user.displayName, user.accountId) for user in self.users}

    def validate_roles(self):
        for role in self.project_input.get('roles').values():
            assert role in self.team_members.keys()

    def delete_all_issues(self):
        deleted_issues = []
        if self.epic:
            deleted_issues.append(self.epic.key)
            self.epic.delete()
        for feature in self.features:
            deleted_issues.append(feature.key)
            feature.delete()
        for story in self.stories:
            deleted_issues.append(story.key)
            story.delete()
        return deleted_issues

    def create_epic(self):
        epic_title = f"[Epic {self.project_input['sub_domain']}_{self.project_input['sub_project']}_{self.project_input['year']}{self.project_input['quarter']}] "
        epic_dict = {
            'project': {'key': self.project_key},
            'summary': epic_title + self.project_input['name'],
            'description': self.project_input['description'],
            'issuetype': {'name': 'Epic'},
            'assignee': {'accountId': self.team_members[self.project_input['roles']['product_owner']].account_id},
            'labels': [self.project_input['sub_domain'], self.project_input['sub_project']]
        }
        self.epic = self.jira.create_issue(fields=epic_dict)
        return self.epic

    def create_feature(self, role, summary, assignee):
        feature_title = f"[Feature {self.project_input['sub_domain']}_{self.project_input['sub_project']}_{self.project_input['year']}{self.project_input['quarter']}] "
        feature_dict = {
            'project': {'key': self.project_key},
            'summary': feature_title + summary,
            'description': self.project_input['description'],
            'issuetype': {'name': 'Feature'},
            'assignee': {'accountId': self.team_members[assignee].account_id},
            'labels': [self.project_input['sub_domain'], self.project_input['sub_project']],
            'parent': {'key': self.epic.key}
        }
        feature = self.jira.create_issue(fields=feature_dict)
        self.features.append(feature)
        return feature

    def create_story(self, story_fields, feature):
        story_title = f"[Story {self.project_input['sub_domain']}_{self.project_input['sub_project']}_{self.project_input['year']}{self.project_input['quarter']}] "
        story_dict = {
            'project': {'key': self.project_key},
            'summary': story_title + story_fields['summary'],
            'description': story_fields.get('description', '') + f"\n\nStory Points: {story_fields.get('story_points', '...')}",
            'issuetype': {'name': 'Story'},
            'assignee': {'accountId': feature.fields.assignee.accountId},
            'labels': [self.project_input['sub_domain'], self.project_input['sub_project']],
            'parent': {'key': self.epic.key}
        }
        story = self.jira.create_issue(fields=story_dict)
        self.jira.create_issue_link('Relates', story.key, feature.key)
        # story.update(fields={'customfield_10004': story_fields.get('story_points', 1)}) # dit veld mag niet aangepast worden?

        self.stories.append(story)
        return story
