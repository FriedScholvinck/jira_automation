import os
from collections import OrderedDict

import streamlit as st
import yaml
from dotenv import load_dotenv

from custom_classes import Epic, Feature, Story, JiraProcess
from utils import check_password

st.set_page_config(
    page_title="MOSS+",
    page_icon='assets/amsterdam_logo.png',
    layout="wide",
)

directies = ['Maatschappelijke Voorzieningen', 'Onderwijs', 'Subsidies', 'Sport en Bos']

# base dict for roles and assignments, which will be updated with the selected team members
roles = OrderedDict([
    ('Business Analist', 'Fried'),
    ('Informatie Analist', 'Fried'),
    ('Data Engineer', 'Fried'),
    ('BI-specialist', 'Fried')
])

# load default input (way of working) from yaml file
data = yaml.safe_load(open('data.yaml', 'r'))

# generically create Epic, Feature and Story objects from the yaml file
for epic_data in data.get('epic', []):
    epic = Epic(**epic_data)
    features = []
    for feature_data in epic_data.get('features', []):
        feature = Feature(**feature_data)
        feature.stories = [Story(**story_data) for story_data in feature_data.get('stories', [])]
        features.append(feature)
    epic.features = features

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
    st.session_state['jira_process'] = JiraProcess(domain, username, api_token, project_key, {})
    st.session_state['team_member_names'] = list(st.session_state['jira_process'].users_by_name.keys())
    st.session_state['process_complete'] = False

# get user input in sidebar and main page
sidebar = st.sidebar
sidebar.header('MOSS+ Jira Process Creator')
summary = sidebar.text_input('Epic', epic.summary)
directie = sidebar.radio('MOSS+ Directie', directies, index=3, horizontal=False)
label_toggle = sidebar.toggle('Afkorting als Jira Label', value=True)
if label_toggle:
    label = sidebar.text_input('Projectlabel', epic.label)

description = st.text_area(
    'Omschrijving',
    epic.description,
    height=300
)

with sidebar.container(border=True):
    st.info('Verwachte opleverdatum')
    year = st.radio('Jaar', ['2024', '2025'], horizontal=False)
    quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=False)

# roles horizontally aligned, with a selectbox for each role
cols = st.columns(len(roles))
for i, c in enumerate(cols):
    with c: roles[list(roles.items())[i][0]] = st.selectbox(f'{list(roles.items())[i][0]}', st.session_state['team_member_names'], st.session_state['team_member_names'].index(list(roles.items())[i][1])),

# refill epic with user input
epic.summary = summary
epic.description = description
epic.directie = directie
epic.label = label if label_toggle else None
epic.expected_completion_date = f'{year} {quarter}'
epic.assignee = roles[epic.role][0]

# st.info('De volgende Jira Issues worden aangemaakt:')
st.divider()
with st.expander(f'Epic: {epic.summary} ({epic.label}))'):
    epic


for feature in epic.features:
    with st.container(border=True):
        feature.summary = st.text_input(f"Feature voor {feature.role} ({roles[feature.role][0]})", feature.summary, key=f'feature_{feature.role}')
        feature.description = st.text_area('Beschrijving', feature.description, key=f'feature_description_{feature.role}')
        feature.directie = directie
        feature.assignee = roles[feature.role][0]
        feature.label = label if label_toggle else None

        stories_to_skip = []
        for i, story in enumerate(feature.stories):
            with st.expander(f'{story.summary} ({story.story_points})'):
                if st.checkbox('Include Story', value=True, key=f'story_toggle_{story.summary}'):
                    story.directie = directie
                    story.summary = st.text_input('Titel', story.summary, label_visibility='hidden', key=f'story_summary_{story.summary}')
                    story.description = st.text_area('Beschrijving', story.description, key=f'story_description_{story.summary}')
                    story.story_points = st.slider('Story Points', 1, 8, story.story_points, key=f'story_points_{story.summary}')
                    story.label = label if label_toggle else None
                    
                    # je kan assignee en rol nog aanpassen
                    story.role = st.selectbox('Rol', list(roles.keys()), list(roles.keys()).index(feature.role), key=f'story_role_{story.summary}')
                    story.assignee = st.selectbox('Assignee', st.session_state['team_member_names'], st.session_state['team_member_names'].index(str(roles[story.role][0])), key=f'story_assignee_{story.summary}')
                else:
                    stories_to_skip.append(i)
        feature.stories = [story for i, story in enumerate(feature.stories) if i not in stories_to_skip]

stories = [story for feature in epic.features for story in feature.stories]
c1, c2 = st.columns(2)
with c1: st.metric('Totaal Story Points', sum([story.story_points for story in stories]))
with c2: st.metric('Aantal Stories', len(stories))

# vraag om wachtwoord zodat we niet gespamd worden met Jira issues
if not check_password(st):
    st.stop()

if st.button('Maak Jira Issues'):
    epic_issue = st.session_state['jira_process'].create_issue(epic)
    
    # give each feature the epic key as parent and create the feature issues
    for feature in epic.features:
        feature.parent = epic_issue.key
        feature_issue = st.session_state['jira_process'].create_issue(feature)

        # give each story the feature key as parent and create the story issues
        for story in feature.stories:
            story.parent = feature_issue.key
            story_issue = st.session_state['jira_process'].create_issue(story)

    
    st.success('Process Complete')
    st.session_state['process_complete'] = True
    st.balloons()

if st.session_state['process_complete']:
    if st.session_state['jira_process'].issues != []:
        if st.button('Verwijder alle issues'):
            deleted_issue_keys = st.session_state['jira_process'].delete_all_issues()
            st.success(f'Issues {deleted_issue_keys} verwijderd.')
            st.session_state['process_complete'] = False
