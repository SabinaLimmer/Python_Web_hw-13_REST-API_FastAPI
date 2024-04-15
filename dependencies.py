from fastapi import Depends

from src.database.db import get_db
from src.repository.contacts import ContactsRepository


def get_contacts_repository(db=Depends(get_db)):
    return ContactsRepository(db)