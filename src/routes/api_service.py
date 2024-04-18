from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect import get_db
from sqlalchemy import text
from src.conf import messages

router = APIRouter(prefix='/api_service', tags=['service'])  # Creates a new router for service-related routes


@router.get("/health_checker")
async def healthchecker(db: AsyncSession = Depends(get_db),
                        request_string: str = "SELECT 1") -> dict:
    """
    A route for checking the health of the application.

    Parameters:
        db (AsyncSession): The database session to use.
        request_string (str): The SQL query string to execute, defaults to "SELECT 1".

    Returns:
        dict: A dictionary containing the health check message and operational capability of the database
    """
    try:
        result = await db.execute(text(request_string))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail= messages.DATABASE_IS_NOT_CONFIGURED)
        return {"message": messages.HEALTH_CHECKER}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=messages.ERROR_CONNECTION_TO_DB)


