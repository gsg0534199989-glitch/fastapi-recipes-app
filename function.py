import pyodbc
from error_Handling import DataAccessError, RecordNotFoundError


# --- פונקציות עזר (Helper Functions) ---

def _row_to_dict(cursor, row):
    """ ממיר שורת pyodbc למילון Python רגיל. """
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def _rows_to_list_of_dicts(cursor, rows):
    """ ממיר רשימת שורות pyodbc לרשימה של מילוני Python רגילים. """
    if not rows:
        return []
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


# --- פונקציות גישה למסד נתונים (CRUD) ---

# פונקציה 1: קבלת כל המתכונים שיש לי במסד
def get_all_recipe_names(conn):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")
    try:
        with conn.cursor() as cursor:
            sql_query = """
            SELECT 
              r.recipe_id, 
              r.name
            FROM 
              Recipes r
            ORDER BY 
              r.name;
            """
            cursor.execute(sql_query)
            recipes = cursor.fetchall()

            # ⬅️ תיקון 1: המרת התוצאה לרשימת מילונים
            return _rows_to_list_of_dicts(cursor, recipes)

    except pyodbc.Error as e:
        raise DataAccessError(f"שגיאה בשליפת רשימת המתכונים: {e}")


# פונקציה 2: קבלת מתכון לפי מזהה ID
def get_recipe_by_id(conn, recipe_id):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")
    try:
        with conn.cursor() as cursor:
            sql_query = """
                    SELECT 
                        r.recipe_id, 
                        r.name, 
                        r.preparation_time, 
                        r.difficulty,
                        c.category_name
                    FROM 
                        Recipes r
                    INNER JOIN 
                        Categories c ON r.category_id = c.category_id
                    WHERE 
                        r.recipe_id = ?; 
                    """
            cursor.execute(sql_query, recipe_id)
            recipe = cursor.fetchone()

            # ⬅️ תיקון 2: המרת התוצאה למילון בודד
            return _row_to_dict(cursor, recipe)

    except pyodbc.Error as e:
        raise DataAccessError(f"שגיאה בשליפת נתוני המתכון: {e}")


# פונקציה 3: קבלת מתכונים לפי קטגוריה (הפונקציה שגרמה ל-500)
def get_recipes_by_category_id(conn, category_id):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")
    try:
        with conn.cursor() as cursor:
            sql_quary = """
             SELECT
               r.recipe_id, 
               r.name, 
               r.preparation_time, 
               r.difficulty,
               c.category_name
             FROM 
               Recipes r
             INNER JOIN 
               Categories c ON r.category_id = c.category_id
             WHERE 
               c.category_id = ?; 
             """
            cursor.execute(sql_quary, category_id)
            recipes = cursor.fetchall()

            # ⬅️ תיקון 3: המרת התוצאה לרשימת מילונים (זה פותר את שגיאת ה-500)
            return _rows_to_list_of_dicts(cursor, recipes)

    except pyodbc.Error as e:
        raise DataAccessError(f"שגיאה בשליפת נתוני הקטגוריה: {e}")


# פונקציה 4: הוספת מתכון
def add_recipe(conn, name, category_id, preparation_time, difficulty, serving_size):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")
    try:
        with conn.cursor() as cursor:
            sql_insert = """
            INSERT INTO Recipes (name, category_id, preparation_time, difficulty, serving_size)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(sql_insert,
                           name,
                           category_id,
                           preparation_time,
                           difficulty,
                           serving_size
                           )
        conn.commit()
        return True
    except pyodbc.Error as e:
        conn.rollback()
        raise DataAccessError(f"שגיאה בהוספת מתכון: {e}")


# פונקציה 5: עדכון פרטים במתכון
def update_recipe_details(conn, recipe_id, data_to_update):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")

    if not data_to_update:
        print("⚠️ אזהרה: לא סופקו נתונים לעדכון.")
        return True

    # 1. בניית שאילתת ה-UPDATE הדינמית
    try:
        # ✅ תיקון קל: ודא שלא מעבירים מפתחות לא חוקיים
        valid_cols = data_to_update.keys()
        set_clauses = [f"{col} = ?" for col in valid_cols]
        set_clause_str = ", ".join(set_clauses)

        sql_update = f"""
        UPDATE Recipes
        SET {set_clause_str}
        WHERE recipe_id = ?;
        """
        values = list(data_to_update.values())
        values.append(recipe_id)

    except Exception as e:
        raise DataAccessError(f"שגיאה בבניית שאילתת העדכון: {e}")

    # 2. ביצוע השאילתה ושמירת השינויים (טרנזקציה)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_update, values)

            if cursor.rowcount == 0:
                raise RecordNotFoundError(recipe_id)

            conn.commit()
            return True

    except pyodbc.Error as e:
        conn.rollback()
        raise DataAccessError(f"שגיאה בגישה למסד בעדכון ID {recipe_id}: {e}")


# פונקציה 6: מחיקת מתכון
def delete_recipe(conn, recipe_id):
    if conn is None:
        raise DataAccessError("Connection to the database is inactive.")
    try:
        with conn.cursor() as cursor:
            sql_delete = "DELETE FROM Recipes WHERE recipe_id=?"
            cursor.execute(sql_delete, recipe_id)

            if cursor.rowcount == 0:
                raise RecordNotFoundError(recipe_id)

        conn.commit()
        return True

    except pyodbc.Error as e:
        conn.rollback()
        raise DataAccessError(f"שגיאה במחיקת מתכון ID {recipe_id}: {e}")