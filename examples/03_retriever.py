import os

from langchain_exabase import Exabase, ExabaseRetriever

EXABASE_API_KEY = os.environ["EXABASE_API_KEY"]
EXABASE_BASE_ID = os.getenv("EXABASE_BASE_ID")

client = Exabase(api_key=EXABASE_API_KEY, base_id=EXABASE_BASE_ID)
retriever = ExabaseRetriever(client=client, limit=4)

docs = retriever.invoke("What does the user prefer?")
for doc in docs:
    print(doc.page_content)
