import os

DB_NAME = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "railway"

DATABASE_URI = (
    f"mysql+pymysql://"
    f"{os.getenv('MYSQLUSER')}:"
    f"{os.getenv('MYSQLPASSWORD')}@"
    f"{os.getenv('MYSQLHOST')}:"
    f"{os.getenv('MYSQLPORT')}/"
    f"{DB_NAME}"
)
