from typing import Optional
from pydantic import BaseModel

class Folder(BaseModel):
    name: str
    description: str

class FolderList(BaseModel):
    number: int
    folders: list[Folder]

class BambooBank(BaseModel):
    docID: str
    link: str
    mimeType: str
    AccountType: str
    StatementDate: str
    AccountNumber: int

class BambooBankList(BaseModel):
    number: int
    documents: list[BambooBank]

class BambooBankSearch(BaseModel):
    AccountType: str
    StatementDate: str
    AccountNumber: int