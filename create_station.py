from database.connection import get_db_connection

connection = get_db_connection()

if connection is None:
    print("DATABASE CONNECTION FAILED")
    raise SystemExit

cursor = connection.cursor()

sql = """
INSERT INTO police_stations
(
    station_name,
    district,
    city,
    state
)
VALUES
(
    'Hingna Police Station',
    'Nagpur City',
    'Nagpur',
    'Maharashtra'
)
"""

try:
    cursor.execute(sql)
    connection.commit()
    print("POLICE STATION CREATED")
    print("Station ID:", cursor.lastrowid)

except Exception as e:
    connection.rollback()
    print("ERROR:", e)

finally:
    cursor.close()
    connection.close()