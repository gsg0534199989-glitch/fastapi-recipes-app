
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.concurrency import run_in_threadpool
from function import (
    get_all_recipe_names,
    get_recipe_by_id,
    get_recipes_by_category_id,
    add_recipe,
    update_recipe_details,
    delete_recipe
)
from gemini_functions import get_gemini_response
from sql_connection import create_server_connection
from error_Handling import DataAccessError, RecordNotFoundError
from pydantic import BaseModel
from typing import Optional


# --- מודלים ---
class RecipeCreate(BaseModel):
    name: str
    category_id: int
    prep_time_minutes: int
    difficulty: str
    serving_size: Optional[int] = 1


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    serving_size: Optional[int] = None


class GeminiQuestion(BaseModel):
    question: str


app = FastAPI(title="מערכת ניהול מתכונים 🌟")

origins = [
    "http://localhost:8000", # אם ה-Frontend רץ בפורט אחר
    "http://localhost:3000", # אם משתמשים ב-React או Vue
    "http://127.0.0.1:8000",
]


app.add_middleware(
    CORSMiddleware,
    # הגדרה זו מאפשרת גישה מכל מקום (כולל file:/// ו-null)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- הפניה ל-Docs ---
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


# --- ניהול חיבור למסד ---
async def get_db():
    conn = None
    try:
        # הפעלת פונקציה סינכרונית ב-threadpool
        conn = await run_in_threadpool(create_server_connection)
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        yield conn
    finally:
        if conn:
            # סגירת חיבור כראוי ב-threadpool
            await run_in_threadpool(conn.close)


# --- Endpoints ---

@app.get("/recipes")
async def list_all_recipes(conn=Depends(get_db)):
    try:
        # **הנחה:** הפונקציה get_all_recipe_names מחזירה רשימה של מילונים/מודלים
        recipes = await run_in_threadpool(get_all_recipe_names, conn)
        return {"count": len(recipes), "recipes": recipes}
    except DataAccessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recipes: {e}")


@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, conn=Depends(get_db)):
    try:
        # **הנחה:** הפונקציה get_recipe_by_id מחזירה מילון (dict)
        recipe = await run_in_threadpool(get_recipe_by_id, conn, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail=f"Recipe ID {recipe_id} not found")

        # אם הפונקציה מחזירה מילון, אין צורך לגשת לאינדקסים (כפי שהיה קודם).
        # אם הפונקציה ב-function.py הותאמה להחזיר מילון, התיקון הוא כאן:
        if isinstance(recipe, dict):
            return recipe

        # אם הפונקציה עדיין מחזירה tuple, נסו גישה בטוחה יותר:
        elif isinstance(recipe, (list, tuple)) and len(recipe) >= 5:
            return {
                "id": recipe[0],
                "name": recipe[1],
                "prep_time": recipe[2],
                "difficulty": recipe[3],
                "category": recipe[4]
            }
        else:
            # אם הנתונים לא מגיעים בפורמט צפוי
            raise HTTPException(status_code=500, detail="Database error: Recipe result format is invalid.")


    except DataAccessError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/recipes/category/{category_id}")
async def list_recipes_by_category(category_id: int, conn=Depends(get_db)):
    try:
        # **הנחה:** הפונקציה get_recipes_by_category_id מחזירה רשימה של מילונים
        recipes = await run_in_threadpool(get_recipes_by_category_id, conn, category_id)
        # אם הנתונים חוזרים כמילונים, FastAPI יכולה להמיר אותם ל-JSON בהצלחה
        return {"count": len(recipes), "recipes": recipes}
    except DataAccessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch category recipes: {e}")


@app.post("/recipes/add")
async def add_recipe_endpoint(recipe_data: RecipeCreate, conn=Depends(get_db)):
    try:
        await run_in_threadpool(
            add_recipe,
            conn,
            recipe_data.name,
            recipe_data.category_id,
            recipe_data.prep_time_minutes,
            recipe_data.difficulty,
            recipe_data.serving_size
        )
        return {"message": "Recipe added successfully"}
    except DataAccessError as e:
        raise HTTPException(status_code=400, detail=f"Failed to add recipe: {e}")


@app.put("/recipes/{recipe_id}")
async def update_recipe_endpoint(recipe_id: int, recipe_data: RecipeUpdate, conn=Depends(get_db)):
    # שימוש ב-model_dump() במקום dict() עבור Pydantic V2
    data_to_update = recipe_data.model_dump(exclude_unset=True)
    if not data_to_update:
        return {"message": "No data provided for update."}
    try:
        await run_in_threadpool(update_recipe_details, conn, recipe_id, data_to_update)
        return {"message": f"Recipe ID {recipe_id} updated successfully"}
    except RecordNotFoundError as e:
        # ודא שה-RecordNotFoundError חושף את ה-detail הנכון
        raise HTTPException(status_code=404, detail=str(e))
    except DataAccessError as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {e}")


@app.delete("/recipes/{recipe_id}")
async def delete_recipe_endpoint(recipe_id: int, conn=Depends(get_db)):
    try:
        await run_in_threadpool(delete_recipe, conn, recipe_id)
        return {"message": f"Recipe ID {recipe_id} deleted successfully"}
    except RecordNotFoundError as e:
        # ודא שה-RecordNotFoundError חושף את ה-detail הנכון
        raise HTTPException(status_code=404, detail=str(e))
    except DataAccessError as e:
        raise HTTPException(status_code=400, detail=f"Deletion failed: {e}")


@app.post("/ask_gemini")
async def ask_ai_about_baking(query: GeminiQuestion):
    try:
        # עטיפה ב-threadpool אם הפונקציה סינכרונית
        response_text = await run_in_threadpool(get_gemini_response, query.question)
        return {"question": query.question, "answer": response_text}
    except DataAccessError as e:
        raise HTTPException(status_code=503, detail=f"AI Service Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unknown error occurred: {e}")