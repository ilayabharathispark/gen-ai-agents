############################################################
# LangSmith Observability Configuration for Google ADK local
############################################################

from dotenv import load_dotenv

load_dotenv()


################################################################
# LangSmith Observability Configuration for Google ADK cloud run
################################################################

from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk()

#############################################
# This file is mandatory for langsmith tracing
#############################################