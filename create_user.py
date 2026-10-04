from database.connection import get_db_connection

connection = get_db_connection()

if connection is None:
    print("DATABASE CONNECTION FAILED")
    raise SystemExit

cursor = connection.cursor()

sql = """
INSERT INTO users
(
    officer_id,
    officer_name,
    officer_rank,
    username,
    password_hash,
    role,
    station_id
)
VALUES
(
    'OFF001',
    'Rahul Patil',
    'Police Inspector',
    'officer1',
    'admin123',
    'OFFICER',
    1
)
"""

try:
    cursor.execute(sql)
    connection.commit()
    print("TEST OFFICER CREATED")

except Exception as e:
    connection.rollback()
    print("ERROR:", e)

finally:
    cursor.close()
    connection.close()