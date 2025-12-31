import pyodbc


def create_server_connection():

    try:

        conn = pyodbc.connect(
          "DRIVER={ODBC Driver 17 for SQL Server};"
          "SERVER=localhost\\SQLEXPRESS;"
          "DATABASE=MyRecipesDB;"
          "Trusted_Connection=yes"
        )
        print("✅ Connection established successfully.")
        return conn
    except pyodbc.Error as e:
        # הדפסת שגיאה אם החיבור נכשל, יחד עם פרטי השגיאה
        print(f"❌ Database connection error: {e}")
        return None

# --- דוגמה להרצה (אם תרצה לבדוק את החיבור ישירות) ---
if __name__ == "__main__":
    connection = create_server_connection()
    if connection:
        # אם החיבור הצליח, סגור אותו לאחר השימוש
        connection.close()