import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
# By default, use a local SQLite file for ease of use.
# To use SQL Server, set usage to 'MSSQL' and configure connection string.
DB_TYPE = os.getenv("ARGUS_DB_TYPE", "SQLITE") # Options: SQLITE, MSSQL

# MSSQL Configuration (Example for local SQLEXPRESS)
SERVER = 'SCNXCV011733495\SQLEXPRESS'
DATABASE = 'ArgusDB'
# For Windows Authentication (Trusted_Connection=yes)
CONNECTION_STRING = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

# -----------------------------------------------------------------------------
# ENGINE SETUP
# -----------------------------------------------------------------------------
if DB_TYPE == "MSSQL":
    # SQL Server Connection
    params = urllib.parse.quote_plus(CONNECTION_STRING)
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"
    print(f"🔌 Connecting to SQL Server: {SERVER}/{DATABASE}")
else:
    # SQLite Connection (Default)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "argus.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    print(f"Connecting to SQLite: {DB_PATH}")

engine = create_engine(DATABASE_URL, echo=True) # echo=True prints SQL queries to console

# -----------------------------------------------------------------------------
# SESSION FACTORY
# -----------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
