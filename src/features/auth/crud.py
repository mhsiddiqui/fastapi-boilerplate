from fastcrud import FastCRUD

from ..auth.models import TokenBlacklist
from .schemas import TokenBlacklistCreate, TokenBlacklistUpdate

CRUDTokenBlacklist = FastCRUD[TokenBlacklist, TokenBlacklistCreate, TokenBlacklistUpdate, TokenBlacklistUpdate, None]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
