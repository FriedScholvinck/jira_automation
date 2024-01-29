# Jira process automation voor datateam MOSS+

This python app leverages the Jira API to automate the creation of Jira issues for a BI team that has a standard way of working. By using this tool, we are able to automatically create most of the stories and subtasks we need to finish a feature (Epic in Jira terms) and assign them to the right people. This saves us a lot of time and reduces the chance of human error. It also helps us to standardize our way of working.

The project is specifically tailored to our infrastructure and way of working, as well as custom implementation of Jira and the SAFe framework. It can be adapted to other teams and projects, but that will require some work.

Our default or standard issues for a project are not defined in the Python code, but in yaml format in the [data](app/data/) folder

Python Streamlit is used as a frontend tool for the project, which enables the user to modify some default values and things like project codes, stakeholder departments, etc... This way, everyone in my team can interact with the Jira API in a user-friendly way, specifically tailored to our needs.

## Project structure
The project is structured as follows:
```
├── app
│   ├── data
│   │   ├── default_issues.yaml
│   ├── main.py (streamlit app)
│   ├── requirements.txt
│   ├── custom_classes.txt (jira api functionality)
│   └── utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

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
Run the project locally using python 3.11.6 or docker. If you have docker installed, simply run `docker compose up` and check the app on `http://localhost:8501/`.

For local development, create a virtual environment and install the requirements. For example:
```
python -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the following command to start the streamlit app locally.
```
streamlit run app/main.py
```

## Deployment

### Streamlit Cloud
The app is deployed on Streamlit Cloud, which is connected to my GitHub account. It automatically deploys the app when a new commit is pushed to the main branch.
Provide environment variables during deployment on Streamlit Cloud.

### Azure
For use in the infrastructure of the datateam, we deploy the app as a docker container on Azure through Azure Devops Pipelines.
