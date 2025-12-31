import os
from google import genai
from google.genai.errors import APIError
from error_Handling import DataAccessError
from dotenv import load_dotenv # 👈 ייבוא נדרש

# 🛑 תיקון: טוען את הקובץ .env מיד עם ייבוא הקובץ הזה 🛑
load_dotenv()
# --------------------------------------------------------

# 1. קרא/י את המפתח ישירות
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise Exception("❌ מפתח Gemini API אינו מוגדר כמשתנה סביבה (GEMINI_API_KEY). אנא בדוק את קובץ .env.")

# 2. העבר/י את המפתח מפורשות ללקוח
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except ValueError as e:
    raise Exception(f"❌ שגיאה בהגדרת Gemini API Key: {e}")

# הפרומפט המגביל (System Prompt)
SYSTEM_PROMPT = (
    "אתה עוזר וירטואלי מומחה במתכונים ואפייה. "
    "ענה רק על שאלות הקשורות למתכונים, אפייה, מרכיבים או בישול. "
    "אם השאלה אינה רלוונטית לתחום זה, ענה בנימוס שאתה יכול לעזור רק בנושאי אוכל ואפייה."
)

def get_gemini_response(user_question: str) -> str:
    """שולח שאלה למודל Gemini ומחזיר את התשובה."""
    try:
        config = {
            "system_instruction": SYSTEM_PROMPT
        }

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_question,
            config=config
        )

        return response.text

    except APIError as e:
        raise DataAccessError(f"Gemini API Error: {e}")
    except Exception as e:
        raise DataAccessError(f"An unexpected error occurred with Gemini: {e}")