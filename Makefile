dev:
	streamlit run main.py

build:
	docker build -t moss-jira-app .

run:
	docker run -p 8501:8501 moss-jira-app

