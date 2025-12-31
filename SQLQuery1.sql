
CREATE DATABASE MyRecipesDB;
use MyRecipesDB
-- *** 1. יצירת טבלאות (SCHEMA) ***

-- 1.1 טבלת Categories
CREATE TABLE Categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(100) NOT NULL UNIQUE
);

-- 1.2 טבלת Ingredients
CREATE TABLE Ingredients (
    ingredient_id INT IDENTITY(1,1) PRIMARY KEY,
    ingredient_name NVARCHAR(255) NOT NULL UNIQUE
);

-- 1.3 טבלת Recipes
CREATE TABLE Recipes (
    recipe_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE,
    preparation_time NVARCHAR(50),
    servings INT,
    instructions NVARCHAR(MAX) NOT NULL,
    difficulty NVARCHAR(50),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- 1.4 טבלת RecipeIngredients (טבלת קישור)
CREATE TABLE RecipeIngredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity NVARCHAR(50) NOT NULL,
    unit NVARCHAR(50),
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);


-- *** 2. הכנסת נתונים (SAMPLE DATA) ***

-- 2.1 הכנסת קטגוריות וקבלת המפתחות שלהן
SET IDENTITY_INSERT Categories ON;
INSERT INTO Categories (category_id, category_name) VALUES 
(1, N'עוגות'), 
(2, N'מרקים'),
(3, N'סלטים');
SET IDENTITY_INSERT Categories OFF;

-- 2.2 הכנסת רכיבים וקבלת המפתחות שלהם
SET IDENTITY_INSERT Ingredients ON;
INSERT INTO Ingredients (ingredient_id, ingredient_name) VALUES 
(1, N'קמח'), 
(2, N'ביצים'), 
(3, N'סוכר'), 
(4, N'שמן'), 
(5, N'שוקולד'),
(6, N'עגבניות'), 
(7, N'בצל'), 
(8, N'עדשים אדומות'),
(9, N'מים'),
(10, N'מלפפונים'),
(11, N'גבינה בולגרית');
SET IDENTITY_INSERT Ingredients OFF;


-- 2.3 הכנסת מתכונים (Recipes)
SET IDENTITY_INSERT Recipes ON;
INSERT INTO Recipes (recipe_id, name, preparation_time, servings, instructions, difficulty, category_id) VALUES 
(101, N'עוגת שוקולד בחושה קלאסית', N'50 דקות', 10, 
N'1. מחממים תנור ל-180 מעלות. 2. מערבבים את כל החומרים הרטובים, מוסיפים את היבשים. 3. אופים 35 דקות. 4. מצננים ומקשטים.', 
N'קל', 1),

(102, N'מרק עדשים אדומות טורקי', N'40 דקות', 6, 
N'1. מטגנים בצל ומוסיפים עדשים. 2. מכסים במים ומביאים לרתיחה. 3. מבשלים עד לריכוך ומטבלים.', 
N'בינוני', 2),

(103, N'סלט יווני קלאסי', N'15 דקות', 4, 
N'1. חותכים את כל הירקות. 2. מוסיפים גבינה ושמן זית. 3. מערבבים בעדינות ומגישים.', 
N'קל', 3);
SET IDENTITY_INSERT Recipes OFF;


-- 2.4 קישור רכיבים למתכונים (RecipeIngredients)

-- מתכון 101: עוגת שוקולד קלאסית
INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity, unit) VALUES 
(101, 1, N'2', N'כוסות'),  -- קמח
(101, 2, N'3', N'יחידות'), -- ביצים
(101, 3, N'1', N'כוס'),    -- סוכר
(101, 4, N'0.5', N'כוס'),  -- שמן
(101, 5, N'100', N'גרם');  -- שוקולד

-- מתכון 102: מרק עדשים טורקי
INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity, unit) VALUES 
(102, 7, N'1', N'יחידה'),  -- בצל
(102, 8, N'1', N'כוס'),    -- עדשים אדומות
(102, 9, N'6', N'כוסות');  -- מים

-- מתכון 103: סלט יווני
INSERT INTO RecipeIngredients (recipe_id, ingredient_id, quantity, unit) VALUES 
(103, 6, N'4', N'יחידות'),   -- עגבניות
(103, 10, N'2', N'יחידות'),  -- מלפפונים
(103, 11, N'200', N'גרם');   -- גבינה בולגרית

-- בדיקה: שאילתה להצגת כל המתכונים שהכנסנו (בדיקה קצרה)
SELECT * FROM Recipes;
SELECT * FROM Categories;