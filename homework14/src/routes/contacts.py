from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session

from src.database.db import SessionLocal
from src.repository.contacts import (get_contacts, create_contact, get_contact, update_contact, delete_contact,
                                     get_contacts_by_search, get_birthdays)
from src.schemas import ContactCreate, ContactUpdate, ContactResponse
from typing import List

from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_contact_endpoint(request: Request, contact: ContactCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new contact.

    :param request: Request, the request context
    :param contact: ContactCreate, the schema defining the contact to create
    :param db: Session, the database session
    :return: The created contact with HTTP 201 status
    """
    return create_contact(db, contact)


@router.get("/", response_model=List[ContactResponse])
@limiter.limit("5/minute")
def read_contacts(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve a list of all contacts with optional pagination.

    :param request: Request, the request context to access various request-specific data
    :param db: Session, the database session
    :return: A list of contacts in the database, subjected to rate limiting
    """
    return get_contacts(db)


@router.get("/{contact_id}", response_model=ContactResponse)
@limiter.limit("5/minute")
def read_contact(request: Request, contact_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single contact by its ID.

    :param request: Request, the request context
    :param contact_id: int, the unique identifier of the contact
    :param db: Session, the database session
    :return: The requested contact or a 404 error if not found
    """
    return get_contact(db, contact_id)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact_endpoint(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    """
    Update an existing contact's information.

    :param contact_id: int, the unique identifier of the contact to be updated
    :param contact: ContactUpdate, the schema instance containing the new data for the contact
    :param db: Session, the database session
    :return: The updated contact, or a 404 error if the contact does not exist
    """
    updated_contact = update_contact(db, contact_id, contact)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@router.delete("/{contact_id}")
def delete_contact_endpoint(contact_id: int, db: Session = Depends(get_db)):
    """
    Delete a contact by its ID.

    :param contact_id: int, the unique identifier of the contact to be deleted
    :param db: Session, the database session
    :return: A message indicating successful deletion or a 404 error if the contact does not exist
    """
    if not delete_contact(db, contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}


@router.get("/search/")
def search_contact_endpoint(query: str, db: Session = Depends(get_db)):
    """
    Search for contacts by a query string that matches first name, last name, or email.

    :param query: str, the search query string
    :param db: Session, the database session
    :return: A list of contacts that match the query
    """
    contacts = get_contacts_by_search(db, query)
    return contacts


@router.get("/birthdays/")
@limiter.limit("5/minute")
def get_birthdays_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve contacts who have birthdays within the next week.

    :param request: Request, the request context
    :param db: Session, the database session
    :return: A list of contacts with upcoming birthdays
    """
    contacts = get_birthdays(db)
    return contacts
