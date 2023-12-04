import os

import streamlit as st
from dotenv import load_dotenv

from jira_classes import JiraProcess

st.set_page_config(
    page_title="MOSS+",
    page_icon="❌",
)

import hmac

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
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Load environment variables
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
st.title('MOSS+ Jira Process Creator')

directies = ['Maatschappelijke Voorzieningen', 'Onderwijs', 'Subsidies', 'Sport en Bos']
directies_kort = ['MV', 'ON', 'SUB', 'S&B']
directies_dict = dict(zip(directies_kort, directies))

name = st.text_input('Naam Dashboard', 'Test Dashboard')
directie = st.radio('MOSS+ Directie', directies, index=3, horizontal=True)
sub_project = st.text_input('Afkorting Project (wordt weergegeven in de titel)', 'TP1')
description = st.text_area('Omschrijving', 'Dit is een test project om het proces van datateam MOSS+ te automatiseren in Jira.')
year = st.radio('Jaar', ['2024', '2025'], index=0, horizontal=True)
quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=True)


# team roles with dropdown for team members
roles = {
    'product_owner': st.selectbox('Product Owner', st.session_state['team_member_names'], index=st.session_state['team_member_names'].index('Fried')),
    'business_analist': st.selectbox('Business Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'informatie_analist': st.selectbox('Information Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'data_engineer': st.selectbox('Data Engineer', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'bi_specialist': st.selectbox('BI Specialist', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
}

icons = {
    'product_owner': '👑',
    'business_analist': '📝',
    'informatie_analist': '👨‍💻',
    'data_engineer': '🛠️',
    'bi_specialist': '📊'
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

story_points_field = 'customfield_10004'

if st.button('Jira Process'):
    st.session_state['jira_process'].project_input = project_input 
    epic_issue = st.session_state['jira_process'].create_epic()
    st.success(f"Epic Created: [{epic_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{epic_issue.key})", icon=icons['product_owner'])

    features = [
        {
            'role': 'business_analist',
            'summary': f'Requirements opstellen voor {name}',
            'assignee': roles['business_analist'],
            'stories': [
                {
                    'summary': f'Ophalen en documenteren requirements voor {name}',
                    'description': 'Requirements ophalen en documenteren.',
                    story_points_field: 4,
                },
                {
                    'summary': f'Dashboard mockup bespreken met stakeholders',
                    'description': 'Functioneel ontwerp opstellen en voorleggen aan stakeholders.',
                    story_points_field: 2,
                },
                {
                    'summary': f'Acceptatiecriteria opstellen.',
                    'description': 'Acceptatiecriteria opstellen.',
                    story_points_field: 4,
                },
                {
                    'summary': 'Presenteren dashboard aan stakeholders',
                    'description': 'Dashboard presenteren aan stakeholders.',
                    story_points_field: 2,
                }
            ]
        },
        {
            'role': 'informatie_analist',
            'summary': f'Informatiemodellen voor {name} opstellen',
            'assignee': roles['informatie_analist'],
            'stories': [
                {
                    'summary': f'Conceptueel model opstellen',
                    'description': 'Vanuit de requirements een conceptueel model opstellen.',
                    story_points_field: 1,
                },
                {
                    'summary': f'EDA uitvoeren',
                    'description': 'Eerste verkenning en mapping van de data.',
                    story_points_field: 2,
                },
                {
                    'summary': f'Logisch model opstellen',
                    'description': 'Vanuit het conceptueel model en de data een logisch model opstellen.',
                    story_points_field: 4,
                },
                {
                    'summary': f'Documentatie',
                    'description': 'Het informatiemodel documenteren.',
                    story_points_field: 2,
                },
                {
                    'summary': 'Validatie data pipeline.',
                    'description': 'Het testen van de data in zilver en goud.',
                    story_points_field: 1,
                },
                {
                    'summary': 'Troubleshooten data pipeline',
                    'description': 'Het troubleshooten van de data pipeline.',
                    story_points_field: 2,
                },
                {
                    'summary': 'Fixen data pipeline',
                    'description': 'Het fixen van de data pipeline.',
                    story_points_field: 1,
                }
            ]
        },
        {
            'role': 'data_engineer',
            'summary': f'Ontwikkelen data pipeline voor {name}',
            'assignee': roles['data_engineer'],
            'stories': [
                {
                    'summary': f'Data inladen (brons)',
                    story_points_field: 4,
                    'description': 'Bron inladen (via landingzone of direct) in de bronze laag van Databricks.'
                },
                {
                    'summary': f'Data verwerken (zilver)',
                    story_points_field: 4,
                    'description': 'Data verwerken en transformaties toepassen in de bronzen laag van Databricks.'
                },
                {
                    'summary': f'Data klaarzetten (goud)',
                    story_points_field: 2,
                }
            ]
        },
        {
            'role': 'bi_specialist',
            'summary': f'Ontwikkeling dashboard {name}',
            'assignee': roles['bi_specialist'],
            'stories': [
                {
                    'summary': 'EDA',
                    'description': 'Dataverkenning in Databricks aan de hand van de conceptuele en logische informatiemodellen van de informatieanalist.',
                    story_points_field: 1,
                },
                {
                    'summary': 'Dashboard ontwikkelen v0.1',
                    'description': 'Eerste versie van het dashboard ontwikkelen in Tableau / Power BI.',
                    story_points_field: 4,
                },
                {
                    'summary': 'Dashboard testen',
                    'description': 'Dashboard testen met stakeholders.',
                    story_points_field: 2,
                },
                {
                    'summary': 'Dashboard documenteren',
                    'description': 'Dashboard documenteren.',
                    story_points_field: 1,
                }
            ]
        }
    ]

    for feature in features:
        feature_issue = st.session_state['jira_process'].create_feature(feature['role'], feature['summary'], feature['assignee'])
        st.success(f"Feature Created: [{feature_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{feature_issue.key}): {feature_issue.fields.summary}", icon=icons[feature['role']])
        for story in feature.get('stories', []):
            story_issue = st.session_state['jira_process'].create_story(story, feature_issue)
            st.success(f"Story Created: [{story_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{story_issue.key}): {story_issue.fields.summary}", icon=icons[feature['role']])
    
    st.success('Process Complete')
    st.session_state['process_complete'] = True

if st.session_state['process_complete']:
    if st.session_state['jira_process'].epic:
        if st.button('Verwijder alle issues'):
            deleted_issues = st.session_state['jira_process'].delete_all_issues()
            st.success(f'Issues {deleted_issues} verwijderd')
            st.session_state['process_complete'] = False
