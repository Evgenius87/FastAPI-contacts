from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactsModel, ContactsResponse, ContactsStatusUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_servise

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactsResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_servise.get_current_user)):
    """
    Returns a list of contacts.
    It takes in an optional skip and limit parameter to paginate the results.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of contact objects
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contacts_id}", response_model=ContactsResponse)
async def read_contact(contacts_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_servise.get_current_user)):
    """
    Returns a contact by its id.
    If the user is not logged in, it will return an error message.
    If the user is logged in but does not have access to this contact, it will return an error message.

    :param contact_id: int: Identify the contact that is to be read
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A contact object
    """
    contact = await repository_contacts.get_contact(contacts_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


@router.post("/", response_model=ContactsResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactsModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_servise.get_current_user)):
    """
    Creates a new contact in the database.
    The function takes a ContactModel object as input, and returns the newly created contact.

    :param body: ContactModel: Validate the data that is passed to the function
    :param db: Session: Get the database connection from the dependency injection
    :param current_user: User: Get the user_id from the token
    :return: A contactmodel object, which is a pydantic model
    """
    return await repository_contacts.create_contact(body,current_user, db)


@router.put("/{contact_id}", response_model=ContactsResponse)
async def update_contact(body: ContactsModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_servise.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact

@router.patch("/{note_id}", response_model=ContactsResponse)
async def update_status_note(body: ContactsStatusUpdate, contact_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(auth_servise.get_current_user)):
    """
    Updates a contact in the database.
        The function takes three arguments:
            - body: A ContactModel object containing the new values for the contact.
            - contact_id: An integer representing the id of an existing contact to be updated.
            - db (optional): A Session object used to connect to and query a database, defaults to None if not provided by caller.

        The function returns a ContactModel object containing all fields from body as well as any other fields that were not included in body but are present on this particular instance of ContactModel.

    :param body: ContactModel: Pass the contact information to be updated
    :param contact_id: int: Identify the contact to be updated
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the auth_service
    :return: A contactmodel object
    """
    contact = await repository_contacts.update_status_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactsResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_servise.get_current_user)):
    """
    Removes a contact from the database.
    The function takes in an integer representing the id of the contact to be removed,
    and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the contact id of the contact to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


