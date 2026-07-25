from dotenv import load_dotenv

load_dotenv()

from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk()

#############################################
#this file is mandatory for langsmith tracing
#############################################