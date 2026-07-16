from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from database.session import get_session
from models.book import Book, BookCreate, BookUpdate

# This must be at the top level (no indentation)
app = FastAPI(title="Bookstore API", version="1.0.0")
