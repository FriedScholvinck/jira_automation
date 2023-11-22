from jira import JIRA

username = 'mymail'
api_token = 'mytoken'
domain = 'mydomain'
jira_url = f'https://{domain}.atlassian.net'

jira_options = {'server': jira_url}
jira = JIRA(options=jira_options, basic_auth=(username, api_token))


project_key = 'myproject'
project = jira.project(project_key)

def get_team_members(project):
    ''' Get all team members in a project and return a dictionary with key = name and value = accountId 
    '''
    team_members = set()
    
    # Fetch issues in the project and add assignees to the team_members set
    for issue in jira.search_issues(f'project={project.key}', maxResults=1000):
        if issue.fields.assignee:
            team_members.add(issue.fields.assignee)

    # get all team members in dictionary with key = name and value = accountId, also get the role of the team member
    team_members_dict = {}
    for team_member in team_members:
        team_members_dict[team_member.displayName.split(' ')[0]] = team_member.accountId    

    return team_members_dict

team = get_team_members(project)
team

project_input = {
    'name': 'Test Dashboard',
    'sub_domain': 'S&B', # kies 1 van ['MV', 'ON', 'SUB', 'S&B']
    'sub_project': 'TD1',
    'description': 'Dit is een test dashboard.',
    'year': '24',
    'quarter': 'Q1',
    'roles': {
        'business_analist': 'Persoon1',
        'informatie_analist': 'Persoon2',
        'data_engineer': 'Persoon3',
        'bi_specialist': 'Persoon4',
    }
}

# assert that all names are in the team keys
for role in project_input.get('roles').values():
    assert role in team.keys()

epic_base_title = f"[Epic {project_input['sub_domain']}_{project_input['sub_project']}_{project_input['year']}{project_input['quarter']}]"
feature_base_title = f"[Feature {project_input['sub_domain']}_{project_input['sub_project']}_{project_input['year']}{project_input['quarter']}]"
story_base_title = f"[{project_input['sub_domain']}_{project_input['sub_project']}_{project_input['year']}{project_input['quarter']}]"

epic_dict = {
    'issuetype': {'name': 'Epic'},
    'summary': epic_base_title + name,
    'description': project_input['description'],
    'project': {'key': project_id},
    'labels': [project_input['sub_domain'], project_input['sub_project']]
}

epic_issue = jira.create_issue(fields=epic_dict)
print(f"Epic Created: {epic_issue.key}")

feature_base_dict = {
    'project': {'id': project_id},
    'summary': feature_base_title,
    'description': project_input['description'],
    'issuetype': {'name': 'Feature'},
    'assignee': {'accountId': project_input.get('roles')['business_analist']},
    'labels': [project_input['sub_domain'], project_input['sub_project']]
}

roles = ['business_analist', 'informatie_analist', 'data_engineer', 'bi_specialist']
features = [
    {
        'role': roles[0],
        'summary': f'{feature_base_title} Requirements opstellen voor {project_input['name']}',
        'assignee': project_input.get('roles')[roles[0]]
    },
    {
        'role': roles[1],
        'summary': f'{feature_base_title} Informatiemodellen voor {project_input['name']}',
        'assignee': project_input.get('roles')[roles[1]]
    },
    {
        'role': roles[2],
        'summary': f'{feature_base_title} Ontwikkelen data pipeline voor {project_input['name']}',
        'assignee': project_input.get('roles')[roles[2]]
    },
    {
        'role': roles[3],
        'summary': f'{feature_base_title} Ontwikkeling dashboard {project_input['name']}',
        'assignee': project_input.get('roles')[roles[3]]
    }
]

jira_features_keys = {}
for feature in features:
    feature_dict = feature_base_dict.copy()
    feature_dict.update(feature)
    feature_issue = jira.create_issue(fields=feature_dict)
    print(f"Feature Created: {feature_issue.key}")
    jira_features[feature_dict['role']] = feature_issue.key


story_base_dict = {
    'project': {'id': project_id},
    'summary': story_base_title,
    'description': project_input['description'],
    'issuetype': {'name': 'Story'},
    'labels': [project_input['sub_domain'], project_input['sub_project']]
}