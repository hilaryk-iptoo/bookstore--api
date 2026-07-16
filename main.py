from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from database.session import get_session
from models.book import Book, BookCreate, BookUpdate

app = FastAPI(title="Bookstore API", version="1.0.0")

# -------------------
# BOOK CRUD ENDPOINTS
# -------------------

@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    existing = session.exec(select(Book).where(Book.isbn == book.isbn)).first()
    if existing:
        raise HTTPException(400, "Book with this ISBN already exists")

    db_book = Book(**book.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """List all books with optional filters"""
    query = select(Book)

    if author:
        query = query.where(Book.author.contains(author))
    if min_price is not None:
        query = query.where(Book.price >= min_price)
    if max_price is not None:
        query = query.where(Book.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.where(Book.stock > 0)
        else:
            query = query.where(Book.stock == 0)

    return session.exec(query.offset(skip).limit(limit)).all()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a specific book by ID"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    """Update a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(book, key, value)
    book.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    """Delete a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    session.delete(book)
    session.commit()
    return None


@app.get("/books/search", response_model=List[Book])
def search_books(q: str, session: Session = Depends(get_session)):
    """Search books by title or author"""
    query = select(Book).where(
        (Book.title.contains(q)) | (Book.author.contains(q))
    )
    return session.exec(query).all()
