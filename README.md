# Jira process automation voor datateam MOSS+

## Getting Started
Clone the repository to your local machine and add a `.env` file to the root of the project. The `.env` file should contain the following variables. The api token can be generated in your Jira account settings.

```
JIRA_DOMAIN='gemeente-amsterdam'
JIRA_USERNAME='your-email'
JIRA_API_TOKEN='your-api-token'
JIRA_PROJECT_KEY='your-project-key' (e.g. 'DSO')
```

## Development
Run the following command to start the streamlit app locally.
```
streamlit run main.py
```

## Deployment
The app is deployed on Streamlit Cloud, which is connected to my GitHub account. Every time a new commit is pushed to the main branch, the app is automatically deployed.

During deployment on Streamlit Cloud, you can provide environment variables.