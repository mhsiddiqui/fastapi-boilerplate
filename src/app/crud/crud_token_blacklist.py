from fastcrud import FastCRUD

from ..schemas.token import TokenBlacklistCreate, TokenBlacklistUpdate
from ..models.token_blacklist import TokenBlacklist

CRUDTokenBlacklist = FastCRUD[TokenBlacklist, TokenBlacklistCreate, TokenBlacklistUpdate, TokenBlacklistUpdate, None]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
