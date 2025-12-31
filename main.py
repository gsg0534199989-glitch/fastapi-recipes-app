#הקובץ המרכזי לפני בנית השרת עם FAST API

# 1. ייבוא המודולים הדרושים
import pyodbc
from sql_connection import create_server_connection  # נניח שזה קובץ החיבור
from function import *  # ייבוא כל פונקציות ה-CRUD (get, add, update, delete)
from error_Handling import RecipeAppError, DataAccessError, RecordNotFoundError
import sys # נשתמש ב-sys.exit במקרה של כשל חיבור קריטי

# --- פונקציית עזר לתפריט ---
def print_menu():
    print("\n\n=== 🌟 מערכת ניהול מתכונים 🌟 ===")
    print("1. הצג את כל המתכונים (שם ו-ID)")
    print("2. הצג מתכון לפי ID")
    print("3. הוסף מתכון חדש")
    print("4. עדכן מתכון קיים (דינמי)")
    print("5. מחק מתכון")
    print("6. הצג מתכונים לפי ID קטגוריה")
    print("0. יציאה")
    print("-------------------------------------")

def handle_add_recipe(conn):
    print("\n--- ➕ הוספת מתכון חדש ---")
    try:
        name =input("שם המתכון:")
        category_id =int(input("category_id(במספר):"))
        prep_time = int(input("זמן הכנה בדקות:"))
        difficulty = input("רמת קושי : (קל/בינוני/קשה)")
        serving_size = int(input("גודל מנה :"))

        add_recipe(conn,name,category_id,prep_time,difficulty,serving_size)
        print(f"✅ המתכון '{name}' נוסף בהצלחה.")

    except ValueError:
        print("❌ קלט לא חוקי. ודא שהכנסת מספרים לשדות המתאימים.")
    except RecipeAppError as e:
        print(f"❌ שגיאה במסד הנתונים: {e}")


def hendle_update_recipe(conn):
    print("\n--- 🔄 עדכון מתכון קיים ---")
    try:
        recipe_id = int(input("הכנס ID של המתכון לעדכון: "))
        column_name = input("הכנס שם עמודה לעדכון (name/difficulty/prep_time_minutes/...): ")
        new_value = input(f"הכנס ערך חדש עבור {column_name}: ")
        data_to_update = {column_name: new_value}
        update_recipe_details(conn, recipe_id, data_to_update)

    except ValueError:
     print("❌ קלט ID לא חוקי.")
    except RecordNotFoundError as e:
     print(f"❌ כשל בעדכון: {e.message}")
    except DataAccessError as e:
     print(f"❌ שגיאה בנתונים: {e}")

def hendle_delete_recipe(conn):
    print("\n--- 🗑️ מחיקת מתכון ---")
    try:
        recipe_id = int(input("הכנס ID של המתכון למחיקה: "))
        delete_recipe(conn, recipe_id)
    except ValueError:
        print("❌ קלט ID לא חוקי.")
    except RecordNotFoundError as e:
        print(f"❌ כשל במחיקה: {e.message}")
    except DataAccessError as e:
        print(f"❌ שגיאה בנתונים: {e}")

#פונקציה ראשית שבודקת חיבור ומריצה את הפונקציות
def run_main_application():
#דבר ראשון צריך לחבר את מסד הנתונים
    conn=None
    try:
        conn = create_server_connection()
        if conn is None:
            print("🔴 לא ניתן להפעיל את האפליקציה: כשל בחיבור למסד הנתונים.")
            sys.exit(1)

        print("✅ החיבור למסד הנתונים נוצר בהצלחה!")
#דבר שני עוברים בלולאה על התפריט
        while True:
            print_menu()
            choice = input("בחר פעולה: ")

            if choice == '1':
                recipes = get_all_recipe_names(conn)
                print("\n--- 📖 רשימת כל המתכונים ---")
                for r in recipes:
                    print(f"ID: {r[0]}, שם: {r[1]}")

            elif choice == '2':
             try:
                recipe_id =int(input("הכנס ID של מתכון:"))
                recipe = get_recipe_by_id(conn, recipe_id)
                if recipe:
                   print(f"שם: {recipe[1]}, זמן: {recipe[2]} דקות, קושי: {recipe[3]}, קטגוריה: {recipe[4]}")
                else:
                    print(f"❌ מתכון ID {recipe_id} לא נמצא.")
             except ValueError:
                print("❌ קלט לא חוקי.")

            elif choice == '3':
                handle_add_recipe(conn)

            elif choice == '4':
                hendle_update_recipe(conn)
            elif choice == '5':
                hendle_delete_recipe(conn)
            elif choice == '6':
                try:
                    category_id = int(input("הכנס ID של הקטגוריה: "))
                    recipes = get_recipes_by_category_id(conn,category_id,)
                    if recipes:
                      print(f"✅ נמצאו {len(recipes)} מתכונים בקטגוריה ID {category_id}")
                      for r in recipes:
                        print(f"ID: {r[0]}, שם: {r[1]}")
                    else:
                        print(f"⚠️ לא נמצאו מתכונים בקטגוריה ID {category_id}.")
                except ValueError:
                 print("❌ קלט לא חוקי.")

            elif choice == '0':
                print("👋 יציאה מהמערכת. ביי!")
                break
            else:
                print("⚠️ בחירה לא חוקית, אנא נסה/י שוב.")

    # 3. טיפול בשגיאות וסגירת חיבור
    except RecipeAppError as e:
        # לוכד את כל שגיאות האפליקציה שהפונקציות זורקות
        print(f"❌ שגיאה קריטית באפליקציה: {e}")

    except Exception as e:
        print(f"❌ אירעה שגיאה בלתי צפויה: {e}")

    finally:
        if conn:
            conn.close()
            print("\n🛬 החיבור למסד הנתונים נסגר.")

if __name__ == '__main__':
    run_main_application()


