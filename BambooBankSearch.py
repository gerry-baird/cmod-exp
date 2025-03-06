from pydantic import BaseModel


class BambooBankSearch(BaseModel):
    AccountType: str
    StatementDate: str
    AccountNumber: int