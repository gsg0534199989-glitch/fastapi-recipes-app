// הגדרת כתובת הבסיס של שרת FastAPI שלך
const API_BASE_URL = 'http://127.0.0.1:8000';

// אלמנטים גלובליים
const recipesDisplay = document.getElementById('recipesDisplay');
const statusMessage = document.getElementById('statusMessage');
const addRecipeForm = document.getElementById('addRecipeForm');
const updateDeleteForm = document.getElementById('updateDeleteForm');
const currentEditIdSpan = document.getElementById('currentEditId');
const editStatus = document.getElementById('editStatus');
// ... אלמנטים גלובליים קודמים
const chatHistory = document.getElementById('chatHistory');
const geminiForm = document.getElementById('geminiForm');
const geminiQuestionInput = document.getElementById('geminiQuestion');
const sendButton = document.getElementById('sendButton');
// ...

// --- פונקציות עזר ---

function showStatus(message, type = 'success', element = statusMessage) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.classList.remove('hidden');
    // הסתרת ההודעה לאחר 5 שניות
    setTimeout(() => {
        element.classList.add('hidden');
    }, 5000);
}

function showTab(tabId) {
    // הסתר את כל התוכן
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    // הסר את האקטיביות מכל הכפתורים
    document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
    
    // הצג את התוכן הנבחר
    document.getElementById(tabId).classList.add('active');
    // סמן את הכפתור הפעיל
    document.querySelector(`.tab-button[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// --- פונקציות CRUD ---

// 1. קריאה: טעינת מתכונים לפי קטגוריה
async function loadRecipesByCategory() {
    const categoryId = document.getElementById('categoryInput').value;
    recipesDisplay.innerHTML = '';
    showStatus(`טוען מתכונים לקטגוריה ID ${categoryId}...`);

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/category/${categoryId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `שגיאה כללית: ${response.status}`);
        }

        if (data.count === 0) {
            recipesDisplay.innerHTML = `<h2>לא נמצאו מתכונים בקטגוריה ID ${categoryId}.</h2>`;
            showStatus('טעינה הסתיימה.', 'success');
            return;
        }

        data.recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'recipe-card';
            card.innerHTML = `
                <h3>${recipe.name}</h3>
                <p><strong>ID:</strong> ${recipe.recipe_id}</p>
                <p><strong>זמן הכנה:</strong> ${recipe.preparation_time} דקות</p>
                <p><strong>קושי:</strong> ${recipe.difficulty}</p>
                <p><strong>קטגוריה:</strong> ${recipe.category_name || 'לא ידוע'}</p>
            `;
            recipesDisplay.appendChild(card);
        });

        showStatus(`נמצאו ${data.count} מתכונים.`);

    } catch (error) {
        recipesDisplay.innerHTML = '';
        showStatus(`כשל בטעינה: ${error.message}`, 'error');
    }
}

// 2. קריאה: טעינת מתכון בודד
async function loadSingleRecipe() {
    const recipeId = document.getElementById('recipeIdInput').value;
    recipesDisplay.innerHTML = '';
    showStatus(`טוען מתכון ID ${recipeId}...`);
    
    if (!recipeId) {
        showStatus('אנא הכנס ID מתכון.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`);
        const data = await response.json();

        if (response.status === 404) {
             throw new Error(`מתכון ID ${recipeId} לא נמצא.`);
        }
        
        if (!response.ok) {
            throw new Error(data.detail || `שגיאה כללית: ${response.status}`);
        }

        const card = document.createElement('div');
        card.className = 'recipe-card single-recipe-card';
        card.innerHTML = `
            <h3>${data.name} (ID: ${data.id})</h3>
            <p><strong>זמן הכנה:</strong> ${data.prep_time} דקות</p>
            <p><strong>רמת קושי:</strong> ${data.difficulty}</p>
            <p><strong>קטגוריה:</strong> ${data.category}</p>
        `;
        recipesDisplay.appendChild(card);
        showStatus(`טעינת מתכון ID ${recipeId} בוצעה בהצלחה.`);

    } catch (error) {
        recipesDisplay.innerHTML = '';
        showStatus(`כשל בטעינת מתכון: ${error.message}`, 'error');
    }
}

// 3. יצירה: הוספת מתכון
addRecipeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    showStatus('מנסה להוסיף מתכון...', 'message');

    const recipeData = {
        name: document.getElementById('addName').value,
        category_id: parseInt(document.getElementById('addCategory').value),
        prep_time_minutes: parseInt(document.getElementById('addTime').value),
        difficulty: document.getElementById('addDifficulty').value,
        serving_size: parseInt(document.getElementById('addServing').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(recipeData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `שגיאה בהוספה: ${response.status}`);
        }

        showStatus(`✅ ${result.message}`, 'success');
        addRecipeForm.reset(); // ניקוי הטופס
    } catch (error) {
        showStatus(`❌ כשל בהוספה: ${error.message}`, 'error');
    }
});

// 4. עדכון/מחיקה: טעינת פרטים לעריכה
async function loadRecipeForEdit() {
    const recipeId = document.getElementById('editIdInput').value;
    editStatus.classList.add('hidden');
    updateDeleteForm.classList.add('hidden');

    if (!recipeId) {
        showStatus('אנא הכנס ID מתכון לעריכה/מחיקה.', 'error', editStatus);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`);
        const data = await response.json();

        if (response.status === 404) {
            throw new Error(`מתכון ID ${recipeId} לא נמצא.`);
        }
        
        if (!response.ok) {
            throw new Error(data.detail || `שגיאה כללית: ${response.status}`);
        }
        
        // מילוי הטופס
        currentEditIdSpan.textContent = recipeId;
        document.getElementById('editName').value = data.name || '';
        document.getElementById('editTime').value = data.prep_time || '';
        document.getElementById('editDifficulty').value = data.difficulty || '';
        // יתר השדות לפי הצורך...

        updateDeleteForm.classList.remove('hidden');
        showStatus(`פרטי מתכון ID ${recipeId} נטענו בהצלחה.`, 'success', editStatus);

    } catch (error) {
        updateDeleteForm.classList.add('hidden');
        showStatus(`כשל בטעינת פרטים: ${error.message}`, 'error', editStatus);
    }
}

// 5. עדכון: שליחת נתוני העדכון
async function handleUpdate() {
    const recipeId = currentEditIdSpan.textContent;
    const updateData = {};
    
    // איסוף רק הנתונים ששוננו (לא ריקים)
    const name = document.getElementById('editName').value;
    const time = document.getElementById('editTime').value;
    const difficulty = document.getElementById('editDifficulty').value;
    
    if (name) updateData.name = name;
    if (time) updateData.prep_time_minutes = parseInt(time);
    if (difficulty) updateData.difficulty = difficulty;
    
    if (Object.keys(updateData).length === 0) {
        showStatus('לא סופקו נתונים לעדכון.', 'error', editStatus);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `שגיאה בעדכון: ${response.status}`);
        }

        showStatus(`✅ ${result.message}`, 'success', editStatus);
    } catch (error) {
        showStatus(`❌ כשל בעדכון: ${error.message}`, 'error', editStatus);
    }
}

// 6. מחיקה: שליחת בקשת מחיקה
async function handleDelete() {
    const recipeId = currentEditIdSpan.textContent;
    if (!confirm(`האם אתה בטוח שברצונך למחוק את מתכון ID ${recipeId}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `שגיאה במחיקה: ${response.status}`);
        }

        showStatus(`✅ ${result.message}`, 'success', editStatus);
        updateDeleteForm.classList.add('hidden'); // הסתרת הטופס לאחר מחיקה
        document.getElementById('editIdInput').value = '';

    } catch (error) {
        showStatus(`❌ כשל במחיקה: ${error.message}`, 'error', editStatus);
    }
}

// --- אתחול ---
// מפעיל את הלשונית הראשונה
document.addEventListener('DOMContentLoaded', () => {
    showTab('view');
});
// פונקציה לבניית בועת צ'אט והוספתה להיסטוריה
function appendMessage(sender, message) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = message;
    chatHistory.appendChild(bubble);

    // גלילה אוטומטית למטה
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
// --- פונקציית צ'אט Gemini ---
geminiForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = geminiQuestionInput.value.trim();

    if (!question) return;

    // 1. הוספת הודעת המשתמש להיסטוריה
    appendMessage('user', question);
    geminiQuestionInput.value = ''; // ניקוי הקלט

    // 2. הצגת אינדיקטור טעינה
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'chat-bubble bot loading';
    loadingMessage.innerHTML = '<span class="loading-indicator"></span> Gemini עונה...';
    chatHistory.appendChild(loadingMessage);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    sendButton.disabled = true; // נעל את הכפתור בזמן טעינה

    try {
        const response = await fetch(`${API_BASE_URL}/ask_gemini`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question }) // שים לב למבנה ה-JSON הנדרש
        });

        const result = await response.json();

        // 3. הסרת הודעת הטעינה
        loadingMessage.remove(); 

        if (!response.ok) {
            // שגיאה (לדוגמה, שגיאת שירות AI 503)
            throw new Error(result.detail || `שגיאת API: ${response.status}`);
        }

        // 4. הוספת תשובת הבוט
        appendMessage('bot', result.answer);

    } catch (error) {
        // הסרת הודעת הטעינה אם היא עדיין קיימת
        if (loadingMessage.parentNode) {
             loadingMessage.remove();
        }

        // הצגת הודעת שגיאה מפורטת
        appendMessage('bot', `❌ שגיאה בחיבור ל-Gemini: ${error.message}`);
    } finally {
        sendButton.disabled = false; // שחרר את הכפתור
    }
});

// --- אתחול (בסוף הקובץ) ---
document.addEventListener('DOMContentLoaded', () => {
    showTab('view');
});