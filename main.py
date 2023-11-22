import os

import streamlit as st
from dotenv import load_dotenv

from jira_classes import JiraProcess

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
    st.session_state['team_member_names'] = list(st.session_state['jira_process'].team_members.keys())
    st.session_state['process_complete'] = False

st.set_page_config(
    page_title="MOSS+",
    page_icon="❌",
)

# Streamlit App
st.title('MOSS+ Jira Process Creator')

name = st.text_input('Naam Dashboard', 'Test Dashboard')
sub_domain = st.radio('Domein', ['MV', 'ON', 'SUB', 'S&B'], index=3, horizontal=True)
sub_project = st.text_input('Afkorting Project', 'TP1')
description = st.text_area('Omschrijving', 'Dit is een test project om het proces van datateam MOSS+ te automatiseren in Jira.')
year = st.radio('Jaar', ['24', '25'], index=0, horizontal=True)
quarter = st.radio('Kwartaal', ['Q1', 'Q2', 'Q3', 'Q4'], horizontal=True)


# team roles with dropdown for team members
roles = {
    'product_owner': st.selectbox('Product Owner', st.session_state['team_member_names'], index=st.session_state['team_member_names'].index('Fried')),
    'business_analist': st.selectbox('Business Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'informatie_analist': st.selectbox('Information Analyst', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'data_engineer': st.selectbox('Data Engineer', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
    'bi_specialist': st.selectbox('BI Specialist', st.session_state['team_member_names'], st.session_state['team_member_names'].index('Fried')),
}

project_input = {
    'name': name,
    'sub_domain': sub_domain,
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
    st.success(f'Epic Created: [{epic_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{epic_issue.key})')

    # Add logic to create features and stories as needed
    features = [
        {
            'role': 'business_analist',
            'summary': f'Requirements opstellen voor {name}',
            'assignee': roles['business_analist'],
            'stories': [
                {
                    'summary': 'Test story 1',
                    story_points_field: 4,
                }
            ]
        },
        {
            'role': 'information_analist',
            'summary': f'Informatiemodellen voor {name} opstellen',
            'assignee': roles['informatie_analist']
        },
        {
            'role': 'data_engineer',
            'summary': f'Ontwikkelen data pipeline voor {name}',
            'assignee': roles['data_engineer'],
            'stories': [
                {
                    'summary': f'Data inladen (brons) voor {name}',
                    story_points_field: 4,
                    'description': 'Bron inladen (via landingzone of direct) in de bronze laag van Databricks.'
                },
                {
                    'summary': f'Data verwerken (zilver) voor {name}',
                    story_points_field: 4,
                    'description': 'Data verwerken en transformaties toepassen in de bronzen laag van Databricks.'
                },
                {
                    'summary': f'Data klaarzetten (goud) voor {name}',
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
                    'summary': f'Ontwikkeling dashboard {name}',
                    story_points_field: 4,
                }
            ]
        }
    ]

    for feature in features:
        feature_issue = st.session_state['jira_process'].create_feature(feature['role'], feature['summary'], feature['assignee'])
        st.success(f'Feature Created: [{feature_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{feature_issue.key}): {feature_issue.fields.summary}')
        for story in feature.get('stories', []):
            story_issue = st.session_state['jira_process'].create_story(story, feature_issue)
            st.success(f'Story Created: [{story_issue.key}]({st.session_state['jira_process'].jira_url}/browse/{story_issue.key}): {story_issue.fields.summary}')
    
    st.success('Process Complete')
    st.session_state['process_complete'] = True

if st.session_state['process_complete']:
    if st.session_state['jira_process'].epic:
        if st.button('Verwijder alle issues'):
            deleted_issues = st.session_state['jira_process'].delete_all_issues()
            st.success(f'Issues {deleted_issues} verwijderd')
