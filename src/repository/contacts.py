from typing import List
from datetime import datetime, date, timedelta

from sqlalchemy import and_, or_, extract
from sqlalchemy.orm import Session

from src.database.models import Contacts, User
from src.schemas import ContactsModel, ContactsUpdate, ContactsStatusUpdate


async def get_contacts(skip: int, limit: int,user: User, db: Session) -> List[Contacts]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param user: User: Filter the contacts by user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    return db.query(Contacts).filter(Contacts.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contacts:
    """
    The get_contact function takes in a database session, contact_id, and user.
    It then queries the database for a Contact with the given id and user_id.
    If it finds one, it returns that Contact object.

    :param contact_id: int: Specify the contact id
    :param user: User: Ensure that the user is logged in and has access to the contact
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    return db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()


async def create_contact(body: ContactsModel, user: User, db: Session) -> Contacts:
    """
    The create_contact function creates a new contact in the database.
        Args:
            body (ContactsModel): The ContactsModel schema model to be created in the database.
            user (User): The User schema model that is creating this contact, used for foreign key relationship with contacts table.
            db (Session): The SQLAlchemy session object.
            
    :param body: ContactsModel: Create a new contact
    :param user: User: Get the user id from the user object
    :param db: Session: Access the database
    :return: The newly created contact
    """
    contact = Contacts(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactsModel, user: User,  db: Session) -> Contacts | None:
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Find the contact in the database
    :param body: ContactsModel: Get the data from the request body
    :param user: User: Ensure that the user is only able to update their own contacts
    :param db: Session: Access the database
    :return: The updated contact
    """
    contact = db.query(Contacts).filter(
        and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.born_date = body.born_date
        db.commit()
    return contact


async def remove_contact(contact_id: int,user: User, db: Session)  -> Contacts | None:
    """
    The remove_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            user (User): The user who is deleting the contact.
            db (Session): The database session to use for querying.

    :param contact_id: int: Specify the contact to delete
    :param user: User: Make sure that the user is authorized to delete the contact
    :param db: Session: Pass the database session to the function
    :return: The deleted contact
    """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def update_status_contact(contact_id: int, body: ContactsStatusUpdate, user: User, db: Session):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Find the contact in the database
    :param body: ContactsStatusUpdate: Get the data from the request body
    :param user: User: Ensure that the user is only able to update their own contacts
    :param db: Session: Access the database
    :return: The updated contact
    """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        contact.done = body.done
        db.commit()
    return contact

def search_contacts(db: Session, query: str, user: User) -> List[Contacts]:
    """
    The search_contacts function searches the database for contacts that match a given query.

    :param db: Session: Access the database
    :param query: str: Search for a contact by first name, last name or email
    :param user: User: Get the user id of the current user
    :return: A list of contacts that match the query
    """
    if not query:
        return []
    return db.query(Contacts).filter(Contacts.user_id == user.id).filter(or_(
        Contacts.first_name.ilike(f"%{query}%"),
        Contacts.last_name.ilike(f"%{query}%"),
        Contacts.email.ilike(f"%{query}%"),
    )).all()


async def get_contacts_with_birthdays(db: Session, user: User):
    """
    The get_contacts_with_birthdays function returns a list of contacts with birthdays in the next week.

    :param db: Session: Pass in the database session
    :param user: User: Get the user_id from the database
    :return: A list of contact objects
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contacts).filter(Contacts.user_id == user.id).filter(
        extract('month', Contacts.born_date) == today.month,
        extract('day', Contacts.born_date) >= today.day,
        extract('day', Contacts.born_date) <= next_week.day
    ).all()
    return contacts