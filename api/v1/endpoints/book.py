from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.book_model import BookModel
from schemas.book_schema import BookSchemaBase, BookSchemaReviews, BookSchemaUpdate

from core.deps import get_session, get_current_user

