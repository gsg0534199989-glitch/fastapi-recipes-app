from sql_connection import create_server_connection

# ניסיון עם Trusted Connection
conn = create_server_connection()
if conn:
    conn.close()

# ניסיון עם SQL Authentication
conn2 = create_server_connection(use_sql_auth=True, uid="api_user", pwd="password123")
if conn2:
    conn2.close()
