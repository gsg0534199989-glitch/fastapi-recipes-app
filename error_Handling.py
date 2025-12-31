
class RecipeAppError(Exception):
    """מחלקת בסיס לשגיאות ספציפיות לאפליקציית המתכונים."""
    pass

class DBConnectionError(RecipeAppError):
    """שגיאה בחיבור הראשוני למסד הנתונים."""
    def __init__(self, message="Connection to the database failed."):
        self.message = message
        super().__init__(self.message)

class DataAccessError(RecipeAppError):
    """שגיאה כללית בגישה למסד (SELECT, INSERT, UPDATE, DELETE)."""
    def __init__(self, message="Error during database operation."):
        self.message = message
        super().__init__(self.message)

class RecordNotFoundError(DataAccessError):
    """שגיאה כשרשומה לא נמצאה (למשל, מחיקה או עדכון של ID לא קיים)."""
    def __init__(self, record_id):
        self.message = f"Record with ID {record_id} not found."
        super().__init__(self.message)