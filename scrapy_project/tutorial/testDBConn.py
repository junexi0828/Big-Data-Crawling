import mariadb
import sys
from scrapy.utils.project import get_project_settings

# Retrieve project settings.
db_params = get_project_settings()["CONNECTION_STRING"]

# Connect to MariaDB: localhost
try:
    conn = mariadb.connect(
        user=db_params["user"],
        password=db_params["password"],
        host=db_params["host"],
        port=db_params["port"],
        database=db_params["database"]
    )

    # Retrieve information
    cursor = conn.cursor()
    cursor.execute("SELECT ID, NAME FROM MY_TEST ORDER BY ID ASC;")
    for id, name in cursor:
        print(f"ID: {id}, NAME: {name}")

    # Insert information
    cursor.execute("INSERT INTO MY_TEST(ID, NAME) VALUES(?, ?)", (id + 1, "Python"))

    # Commit transaction and close connection
    conn.commit()
    conn.close()

except mariadb.Error as e:
    print(f"Error connecting to MariaDB:{db_params['host']} - {e}")
    sys.exit()
