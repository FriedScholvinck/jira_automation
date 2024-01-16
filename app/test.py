import logging

import streamlit as st

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Hello logger")

st.title("Hello Azure Webapp")
st.write("This is a test app for azure webapp")

# import sys
# from streamlit import cli as stcli

# if __name__ == '__main__':
#     sys.argv = ["streamlit", "run", "main.py"]
#     sys.exit(stcli.main())