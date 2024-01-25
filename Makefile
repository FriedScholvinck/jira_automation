dev:
	streamlit run app/main.py

build:
	docker build -t moss-jira-app .

run:
	docker run -p 8501:8501 moss-jira-app

logs:
	az webapp log tail --name moss-jira-app --resource-group rg-dpms-ont-weu-01
