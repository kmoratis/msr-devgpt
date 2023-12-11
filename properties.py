import os
from dotenv import load_dotenv

# Load the stored environment variables
load_dotenv()

dbpath = os.getenv("DBPATH")
datasetpath = os.getenv("DATASETPATH")
githubapikey = os.getenv("GITHUBAPIKEY")
snapshot = os.getenv("WORKINGSNAPSHOT")
pmd = os.getenv("PMDPATH")
java = os.getenv("JAVAPATH")
simian = os.getenv("SIMIANPATH")
resultspath = os.getenv("RESULTSPATH")