import hmac
import os
from collections import OrderedDict

import streamlit as st
import yaml
from dotenv import load_dotenv

from classes import Epic, Feature, Story
from jira_classes import JiraProcess

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
    epic.features = features

# load and apply a custom CSS file
# st.markdown(f"<style>{open('custom.css', 'r').read()}</style>", unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Vul het wachtwoord in om het proces te voltooien", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

# load credentials from .env file
load_dotenv()
domain = os.getenv('JIRA_DOMAIN')
username = os.getenv('JIRA_USERNAME')
api_token = os.getenv('JIRA_API_TOKEN')
project_key = os.getenv('JIRA_PROJECT_KEY')

# check credentials
if not domain and username and api_token and project_key:
    st.error('Jira credentials niet goed geconfigureerd in .env file.')
    st.stop()

# initialize JiraProcess object in session state, otherwise it will be created on every page refresh (whenever a button is clicked)
if not 'jira_process' in st.session_state:
    st.session_state['jira_process'] = JiraProcess(domain, username, api_token, project_key, {})
    st.session_state['team_member_names'] = list(st.session_state['jira_process'].users_by_name.keys())
    st.session_state['process_complete'] = False

# Streamlit App
sidebar = st.sidebar
sidebar.header('MOSS+ Jira Process Creator')
name = sidebar.text_input('Epic', epic.summary)
directie = sidebar.radio('MOSS+ Directie', directies, index=3, horizontal=False)
label_toggle = sidebar.toggle('Afkorting als Jira Label', value=True)
if label_toggle:
    label = sidebar.text_input('Projectlabel', epic.labels[0])

description = st.text_area(
    'Omschrijving',
    epic.description,
    height=300
)

with sidebar.container(border=True):
    st.info('Verwachte opleverdatum')
    year = st.radio('Jaar', ['2024', '2025'], horizontal=False)
    quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=False)



cols = st.columns(len(roles))
for i, c in enumerate(cols):
    with c: roles[list(roles.items())[i][0]] = st.selectbox(f'{list(roles.items())[i][0]}', st.session_state['team_member_names'], st.session_state['team_member_names'].index(list(roles.items())[i][1])),


epic.labels = [label] if label_toggle else None


# st.info('De volgende Jira Issues worden aangemaakt:')
st.divider()
with st.expander(f'Epic: {epic.summary}'):
    epic

for feature in epic.features:
    with st.container(border=True):
        feature.summary = st.text_input(f"Feature voor {feature.role} ({roles[feature.role][0]})", feature.summary, key=f'feature_{feature.role}')
        feature.description = st.text_area('Beschrijving', feature.description, key=f'feature_description_{feature.role}')

        for story in feature.stories:
            with st.expander(f'{story.summary} ({story.story_points})'):
                if st.toggle('Neem deze story niet mee', value=True, key='toggle_1'):
                    story.summary = st.text_input('Titel', story.summary, label_visibility='hidden', key='story_1')
                    story.description = st.text_area('Beschrijving', story.description)
                    story.story_points = st.slider('Story Points', 1, 8, story.story_points, key='story_points_1')
                    
                    # je kan assignee en rol nog aanpassen
                    story.assignee = st.selectbox('Assignee', st.session_state['team_member_names'], st.session_state['team_member_names'].index(roles[story.role][0]))
                    story.role = st.selectbox('Rol', list(roles.keys()), list(roles.keys()).index(feature.role))
                    feature.stories.append(story)


        



total_story_points = sum([story.story_points for feature in epic.features for story in feature.stories])
st.metric('Totaal aantal Story Points', total_story_points)


if not check_password():
    st.stop()  # Do not continue if check_password is not True.
    
if st.button('Maak Jira Issues'):
    st.session_state['jira_process'].project_input = project_input 
    epic_issue = st.session_state['jira_process'].create_epic()
    st.success(f"Epic Created: [{epic_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{epic_issue.key})", icon=icons['Business Analist'])

    features = [
        {
            'role': 'Business Analist',
            'summary': f'Requirements opstellen voor {name}',
            'assignee': roles['Business Analist'],
            'stories': [
                {
                    'summary': f'Ophalen en documenteren requirements voor {name}',
                    'description': 'Requirements ophalen en documenteren.',
                    st.session_state['jira_process'].story_points_field: 4,
                },
                # {
                #     'summary': f'Dashboard mockup bespreken met stakeholders',
                #     'description': 'Functioneel ontwerp opstellen en voorleggen aan stakeholders.',
                #     st.session_state['jira_process'].story_points_field: 2,
                # },
                # {
                #     'summary': f'Acceptatiecriteria opstellen.',
                #     'description': 'Acceptatiecriteria opstellen.',
                #     st.session_state['jira_process'].story_points_field: 4,
                # },
                # {
                #     'summary': 'Presenteren dashboard aan stakeholders',
                #     'description': 'Dashboard presenteren aan stakeholders.',
                #     st.session_state['jira_process'].story_points_field: 2,
                # }
            ]
        },
        # {
        #     'role': 'Informatie Analist',
        #     'summary': f'Informatiemodellen voor {name} opstellen',
        #     'assignee': roles['Informatie Analist'],
        #     'stories': [
        #         {
        #             'summary': f'Conceptueel model opstellen',
        #             'description': 'Vanuit de requirements een conceptueel model opstellen.',
        #             st.session_state['jira_process'].story_points_field: 1,
        #         },
        #         {
        #             'summary': f'EDA uitvoeren',
        #             'description': 'Eerste verkenning en mapping van de data.',
        #             st.session_state['jira_process'].story_points_field: 2,
        #         },
        #         {
        #             'summary': f'Logisch model opstellen',
        #             'description': 'Vanuit het conceptueel model en de data een logisch model opstellen.',
        #             st.session_state['jira_process'].story_points_field: 4,
        #         },
        #         {
        #             'summary': f'Documentatie',
        #             'description': 'Het informatiemodel documenteren.',
        #             st.session_state['jira_process'].story_points_field: 2,
        #         },
        #         {
        #             'summary': 'Validatie data pipeline.',
        #             'description': 'Het testen van de data in zilver en goud.',
        #             st.session_state['jira_process'].story_points_field: 1,
        #         },
        #         {
        #             'summary': 'Troubleshooten data pipeline',
        #             'description': 'Het troubleshooten van de data pipeline.',
        #             st.session_state['jira_process'].story_points_field: 2,
        #         },
        #         {
        #             'summary': 'Fixen data pipeline',
        #             'description': 'Het fixen van de data pipeline.',
        #             st.session_state['jira_process'].story_points_field: 1,
        #         }
        #     ]
        # },
        # {
        #     'role': 'Data Engineer',
        #     'summary': f'Ontwikkelen data pipeline voor {name}',
        #     'assignee': roles['Data Engineer'],
        #     'stories': [
        #         {
        #             'summary': f'Data inladen (brons)',
        #             st.session_state['jira_process'].story_points_field: 4,
        #             'description': 'Bron inladen (via landingzone of direct) in de bronze laag van Databricks.'
        #         },
        #         {
        #             'summary': f'Data verwerken (zilver)',
        #             st.session_state['jira_process'].story_points_field: 4,
        #             'description': 'Data verwerken en transformaties toepassen in de bronzen laag van Databricks.'
        #         },
        #         {
        #             'summary': f'Data klaarzetten (goud)',
        #             st.session_state['jira_process'].story_points_field: 2,
        #         },
        #     ]
        # },
        # {
        #     'role': 'BI-specialist',
        #     'summary': f'Ontwikkeling dashboard {name}',
        #     'assignee': roles['BI-specialist'],
        #     'stories': [
        #         {
        #             'summary': 'EDA',
        #             'description': 'Dataverkenning in Databricks aan de hand van de conceptuele en logische informatiemodellen van de informatieanalist.',
        #             st.session_state['jira_process'].story_points_field: 1,
        #         },
        #         {
        #             'summary': 'Dashboard ontwikkelen v0.1',
        #             'description': 'Eerste versie van het dashboard ontwikkelen in Tableau / Power BI.',
        #             st.session_state['jira_process'].story_points_field: 4,
        #         },
        #         {
        #             'summary': 'Dashboard testen',
        #             'description': 'Dashboard testen met stakeholders.',
        #             st.session_state['jira_process'].story_points_field: 2,
        #         },
        #         {
        #             'summary': 'Dashboard documenteren',
        #             'description': 'Dashboard documenteren.',
        #             st.session_state['jira_process'].story_points_field: 1,
        #         }
        #     ]
        # }
    ]

    for feature in features:
        feature_issue = st.session_state['jira_process'].create_feature(feature['role'], feature['summary'], feature['assignee'])
        st.success(f"Feature Created: [{feature_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{feature_issue.key}): {feature_issue.fields.summary}", icon=icons[feature['role']])
        for story in feature.get('stories', []):
            story_issue = st.session_state['jira_process'].create_story(story, feature_issue)
            st.success(f"Story Created: [{story_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{story_issue.key}): {story_issue.fields.summary}", icon=icons[feature['role']])
    
    st.success('Process Complete')
    st.session_state['process_complete'] = True
    st.balloons()

if st.session_state['process_complete']:
    if st.session_state['jira_process'].epic:
        if st.button('Verwijder alle issues'):
            deleted_issues = st.session_state['jira_process'].delete_all_issues()
            st.success(f'Issues {[issue.key for issue in deleted_issues]} verwijderd.')
            st.session_state['process_complete'] = False
