# Jira process automation voor datateam MOSS+

## Getting Started
Clone the repository to your local machine and add a `.env` file to the root of the project. The `.env` file should contain the following variables. The api token can be generated in your Jira account settings.

```
JIRA_DOMAIN='your-domain'
JIRA_USERNAME='your-email'
JIRA_API_TOKEN='your-api-token'
JIRA_PROJECT_KEY='your-project-key' (e.g. 'DSO')
```

For password protection, you need to include a `secrets.toml` file in a `.streamlit` folder with the following (or comment out the password protection in `app/main.py`).
```
password="your-password"
```

## Development
Run the following command to start the streamlit app locally.
```
streamlit run app/main.py
```

## Deployment

### Streamlit Cloud
The app is deployed on Streamlit Cloud, which is connected to my GitHub account. It automatically deploys the app when a new commit is pushed to the main branch.
Provide environment variables during deployment on Streamlit Cloud.

### Azure