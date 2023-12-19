import os
from collections import OrderedDict

import streamlit as st
import yaml
from dotenv import load_dotenv

from custom_classes import JiraProcess, Epic, Feature, Story, SubTask
from utils import check_password

st.set_page_config(
    page_title="MOSS+",
    page_icon='assets/amsterdam_logo.png',
    layout="wide",
)

YAML_FILE = 'data.yaml'
DIRECTIES = ['Maatschappelijke Voorzieningen', 'Onderwijs', 'Subsidies', 'Sport en Bos']
MAX_STORY_POINTS = 8 # can be overwritten in the yaml file

# base dict for roles and assignments, which will be updated with the selected team members
roles = OrderedDict([
    ('Business Analist', 'Fried'),
    ('Informatie Analist', 'Fried'),
    ('Data Engineer', 'Fried'),
    ('BI-specialist', 'Fried')
])

# load default input (way of working) from yaml file
data = yaml.safe_load(open(YAML_FILE, 'r'))

# generically create story, story and Story objects from the yaml file
for epic_data in data.get('epic', []):
    epic = Epic(**epic_data)
    stories = []
    for story_data in epic_data.get('stories', []):
        story = Story(**story_data)
        story.subtasks = [SubTask(**subtask_data) for subtask_data in story_data.get('subtasks', [])]
        stories.append(story)
    epic.stories = stories

# load credentials from .env file
load_dotenv()
domain = os.getenv('JIRA_DOMAIN')
username = os.getenv('JIRA_USERNAME')
api_token = os.getenv('JIRA_API_TOKEN')
project_key = os.getenv('JIRA_PROJECT_KEY')

# load and apply a custom CSS file
# st.markdown(f"<style>{open('custom.css', 'r').read()}</style>", unsafe_allow_html=True)

# check credentials
if not domain and username and api_token and project_key:
    st.error('Jira credentials niet goed geconfigureerd in .env file.')
    st.stop()

# initialize JiraProcess object in session state, otherwise it will be created on every page refresh (whenever a button is clicked)
if not 'jira_process' in st.session_state:
    with st.spinner('Loading Jira Process...'):
        st.session_state['jira_process'] = JiraProcess(domain, username, api_token, project_key, {})
    st.session_state['team_member_names'] = list(st.session_state['jira_process'].users_by_name.keys())
    st.session_state['process_complete'] = False

# get user input in sidebar and main page
sidebar = st.sidebar
sidebar.header('MOSS+ Jira Process Creator')
summary = sidebar.text_input('Epic', epic.summary)
directie = sidebar.radio('MOSS+ Directie', DIRECTIES, index=3, horizontal=False)
label_toggle = sidebar.toggle('Afkorting als Jira Label', value=True)
if label_toggle:
    label = sidebar.text_input('Projectlabel', epic.label)


with sidebar.container(border=True):
    st.info('Verwachte opleverdatum')
    year = st.radio('Jaar', ['2024', '2025'], horizontal=False)
    quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=False)

description = st.text_area(
    'Omschrijving',
    epic.description.replace('directie', directie) + '\n\nOplevering: ' + f'{year} {quarter}',
    height=400
)

# roles horizontally aligned, with a selectbox for each role
cols = st.columns(len(roles))
for i, c in enumerate(cols):
    with c: roles[list(roles.items())[i][0]] = st.selectbox(f'{list(roles.items())[i][0]}', st.session_state['team_member_names'], st.session_state['team_member_names'].index(list(roles.items())[i][1])),

# refill story with user input
epic.summary = summary
epic.description = description
epic.directie = directie
epic.label = label if label_toggle else None
epic.expected_completion_date = f'{year} {quarter}'
epic.assignee = roles[story.role][0]

# st.info('De volgende Jira Issues worden aangemaakt:')
st.divider()
with st.expander(f'Epic: {epic.summary} ({epic.label}))'):
    epic


for story in epic.stories:
    with st.container(border=True):
        story.summary = st.text_input(f"Story voor {story.role} ({roles[story.role][0]})", story.summary, key=f'story_{story.summary}')
        story.description = st.text_area('Beschrijving', story.description, key=f'story_description_{story.summary}')
        story.directie = directie
        story.assignee = roles[story.role][0]
        story.label = label if label_toggle else None
        story.story_points = st.slider('Story Points', 1, MAX_STORY_POINTS, story.story_points, key=f'story_points_{story.summary}')

        subtasks_to_skip = []
        for i, subtask in enumerate(story.subtasks):
            with st.expander(f'{subtask.summary}'):
                if st.checkbox('Include Sub-task', value=True, key=f'subtask_toggle_{subtask.summary}'):
                    subtask.directie = directie
                    subtask.summary = st.text_input('Titel', subtask.summary, label_visibility='hidden', key=f'subtask_summary_{subtask.summary}')
                    if hasattr(subtask, 'description'):
                        subtask.description = st.text_area('Beschrijving', subtask.description, key=f'subtask_description_{subtask.summary}')
                    subtask.label = label if label_toggle else None
                    
                    # je kan assignee en rol nog aanpassen
                    subtask.role = st.selectbox('Rol', list(roles.keys()), list(roles.keys()).index(story.role), key=f'subtask_role_{subtask.summary}')
                    subtask.assignee = st.selectbox('Assignee', st.session_state['team_member_names'], st.session_state['team_member_names'].index(str(roles[subtask.role][0])), key=f'subtask_assignee_{subtask.summary}')
                else:
                    subtasks_to_skip.append(i)
        story.subtasks = [subtask for i, subtask in enumerate(story.subtasks) if i not in subtasks_to_skip]

c1, c2, c3 = st.columns(3)
with c1: st.metric('Aantal Stories', len(epic.stories))
with c2: st.metric('Totaal Story Points', sum([story.story_points for story in epic.stories]))
with c3: st.metric('Totaal Aantal Subtaken', sum([len(story.subtasks) for story in epic.stories]))

# vraag om wachtwoord zodat we niet gespamd worden met Jira issues
if not check_password(st):
    st.stop()

if st.button('Maak Jira Issues'):
    epic_issue = st.session_state['jira_process'].create_issue(epic)
    st.success(f'Epic [{epic_issue.key}]({epic_issue.permalink()}): {epic.summary}')
    
    # give each story the story key as parent and create the story issues
    for story in epic.stories:
        story.parent = epic_issue.key
        story_issue = st.session_state['jira_process'].create_issue(story)
        st.success(f'Story [{story_issue.key}]({story_issue.permalink()}): {story.summary}')

        # give each story the story key as parent and create the story issues
        for subtask in story.subtasks:
            subtask.parent = story_issue.key

            # cannot create story points in this screen
            if hasattr(subtask, 'story_points'):
                del subtask.story_points

            subtask_issue = st.session_state['jira_process'].create_issue(subtask)
            st.success(f'Sub-task [{subtask_issue.key}]({subtask_issue.permalink()}): {subtask.summary}')

    
    st.success('Process Complete')
    st.session_state['process_complete'] = True
    st.balloons()

if st.session_state['process_complete']:
    if st.session_state['jira_process'].issues != []:
        if st.button('Verwijder alle issues'):
            deleted_issue_keys = st.session_state['jira_process'].delete_all_issues()
            st.success(f'Issues {deleted_issue_keys} verwijderd.')
            st.session_state['process_complete'] = False
