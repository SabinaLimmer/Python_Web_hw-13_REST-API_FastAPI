from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import extract, or_

from src.database.models import Contact
from src.schemas import ContactIn, UserOut, ContactOut
from src.repository.abstract import AbstractContactsRepository

class ContactsRepository(AbstractContactsRepository):
    def __init__(self, db: Session):
        self._db = db

    async def get_contacts(self, skip: int, limit: int, user: UserOut) -> list[ContactOut]:
        return self._db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


    async def get_contact(self, contact_id: int, user: UserOut) -> ContactOut:
        return self._db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()


    async def create_contact(self, body: ContactIn, user: UserOut) -> ContactOut:
        contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email, phone_number = body.phone_number, date_of_birth = body.date_of_birth, user_id=user.id)
        self._db.add(contact)
        self._db.commit()
        self._db.refresh(contact)
        return contact


    async def remove_contact(self, contact_id: int, user: UserOut) -> ContactOut | None:
        contact = self._db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
        if contact:
            self._db.delete(contact)
            self._db.commit()
        return contact


    async def update_contact(self, contact_id: int, body: ContactIn, user: UserOut) -> ContactOut | None:
        contact = self._db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.email = body.email
            contact.phone_number = body.phone_number
            contact.date_of_birth = body.date_of_birth
            self._db.commit()
        return contact


    async def get_contacts_by_query(self, query: str, skip: int, limit: int, user: UserOut) -> list[ContactOut]:
        contact = self._db.query(Contact).filter(Contact.user_id == user.id)
        if query:
            return contact.filter(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%")
                )
            ).offset(skip).limit(limit).all()


    async def get_contacts_with_upcoming_birthdays(self, user: UserOut) -> list[ContactOut]:
        contact = self._db.query(Contact).filter(Contact.user_id == user.id)
        today = datetime.today()
        end_date = today + timedelta(days=7)
        return contact.filter(
            extract('month', Contact.date_of_birth) == today.month,
            extract('day', Contact.date_of_birth) >= today.day,
            extract('day', Contact.date_of_birth) <= end_date.day
        ).all()
