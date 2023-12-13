import hmac
import os

import streamlit as st
from dotenv import load_dotenv

from classes import Epic, Feature, Story
from jira_classes import JiraProcess

st.set_page_config(
    page_title="MOSS+",
    page_icon='assets/amsterdam_logo.png',
)

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

load_dotenv()
domain = os.getenv('JIRA_DOMAIN')
username = os.getenv('JIRA_USERNAME')
api_token = os.getenv('JIRA_API_TOKEN')
project_key = os.getenv('JIRA_PROJECT_KEY')

if not domain and username and api_token and project_key:
    st.error('Jira credentials niet goed geconfigureerd in .env file.')
    st.stop()

if not 'jira_process' in st.session_state:
    st.session_state['jira_process'] = JiraProcess(domain, username, api_token, project_key, {})
    st.session_state['team_member_names'] = list(st.session_state['jira_process'].users_by_name.keys())
    st.session_state['process_complete'] = False


# Streamlit App
directies = ['Maatschappelijke Voorzieningen', 'Onderwijs', 'Subsidies', 'Sport en Bos']
directies_kort = ['MV', 'ON', 'SUB', 'S&B']
directies_dict = dict(zip(directies_kort, directies))

sidebar = st.sidebar
sidebar.header('MOSS+ Jira Process Creator')
name = sidebar.text_input('Epic', 'Test Dashboard')
directie = sidebar.radio('MOSS+ Directie', directies, index=3, horizontal=False)
sub_project = sidebar.text_input('Afkorting Project (Jira Label)', 'Test1')
description = st.text_area(
    'Omschrijving',
    open('description.txt', 'r').read() if os.path.exists('description.txt') else f'Requirements {name}',
    height=300
)

with sidebar.container(border=True):
    st.info('Verwachte opleverdatum')
    year = st.radio('Jaar', ['2024', '2025'], horizontal=False)
    quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=False)


# team roles with dropdown for team members
rollen = ['Business Analist', 'Informatie Analist', 'Data Engineer', 'BI-specialist']
# with st.container(border=True):
col1, col2, col3, col4 = st.columns(4)
with col1: ba = st.selectbox('📝 Business Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
with col2: ia = st.selectbox('👨‍💻 Information Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
with col3: de = st.selectbox('🛠️ Data Engineer', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
with col4: bi = st.selectbox('📊 BI Specialist', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
        
roles = {
    'Business Analist': ba[0],
    'Informatie Analist': ia[0],
    'Data Engineer': de[0],
    'BI-specialist': bi[0]
}

icons = {
    'Business Analist': '📝',
    'Informatie Analist': '👨‍💻',
    'Data Engineer': '🛠️',
    'BI-specialist': '📊'
}

project_input = {
    'name': name,
    'directie': directie,
    'sub_project': sub_project,
    'description': description,
    'year': year,
    'quarter': quarter,
    'roles': roles
}

# st.divider()
st.info('De volgende Jira Issues worden aangemaakt:')
with st.expander(f'Epic: {name} - {sub_project}'):
    epic = Epic(
        f'{name} - {sub_project}',
        st.write('Omschrijving', description),
        directie
    )

with st.container(border=True):
    st.warning(f"Business Analist ({roles['Business Analist']})")
    epic.features.append(
        Feature(
            st.text_input('Feature Titel', f'Requirements opstellen voor {name}'),
            st.text_input('Feature Beschrijving', 'Requirements ophalen en documenteren.'),
            directie
        )
    )
    with st.expander(f'Bijbehorende Stories'):
        epic.features[-1].stories.extend([
            Story(
                st.text_input('Story 1', f'Ophalen en documenteren requirements voor {name}', label_visibility='hidden'),
                st.text_area('Beschrijving', 'Requirements ophalen en documenteren.'),
                directie,
                st.slider('Story Points', 1, 8, 4, key='story_points_1')
            ),
            Story(
                st.text_input('Story 2', f'Dashboard mockup bespreken met stakeholders'),
                st.text_area('Beschrijving', 'Functioneel ontwerp opstellen en voorleggen aan stakeholders.'),
                directie,
                st.slider('Story Points', 1, 8, 2, key='story_points_2')
            )
        ])



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
