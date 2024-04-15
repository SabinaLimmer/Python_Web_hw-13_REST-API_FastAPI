from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

from src.schemas import ContactIn, ContactOut, UserOut
from src.repository.abstract import AbstractContactsRepository
from src.services.auth import auth_service

from dependencies import get_contacts_repository


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactOut], description="No more than 10 requests per minute", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactOut)
async def read_contact(contact_id: int,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


@router.post("/", response_model=ContactOut)
async def create_contact(body: ContactIn,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, current_user)


@router.put("/{contact_id}", response_model=ContactOut)
async def update_contact(body: ContactIn, contact_id: int,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactOut)
async def remove_contact(contact_id: int,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    return contact


@router.get("/search/", response_model=List[ContactOut])
async def search_contacts(query: str, skip: int = 0, limit: int = 100,
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts_by_query(query, skip, limit, current_user)
    return contacts


@router.get("/upcoming-birthdays/", response_model=List[ContactOut])
async def get_contacts_upcoming_birthdays(
                        repository_contacts: AbstractContactsRepository = Depends(get_contacts_repository),
                        current_user: UserOut = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts_with_upcoming_birthdays(current_user)
    return contacts