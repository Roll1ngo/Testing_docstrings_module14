from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect import get_db
from sqlalchemy import text

router = APIRouter(prefix='/api_service', tags=['service'])


@router.get("/health_checker")
async def healthchecker(db: AsyncSession = Depends(get_db)) -> dict:
    """
    A route for checking the health of the application.

    Parameters:
        db (AsyncSession): The database session to use.

    Returns:
        dict: A dictionary containing the health check message and operational capability of the database
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "FastApi is here! Database configured correctly"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


