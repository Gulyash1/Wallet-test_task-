import os
from uuid import UUID

from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status
from wallet.db.connection import get_db
from wallet.db.models import Wallet
from wallet.db.schemas import WalletSchema, WalletOperation
import wallet.utils.wallet.database as util


router = APIRouter(prefix= os.getenv("API_PREFIX"))



@router.post("/create",
            status_code= status.HTTP_201_CREATED,
            response_model=WalletSchema)
async def create_wallet(db: AsyncSession = Depends(get_db)):
    """Create a new wallet."""
    wallet = Wallet(balance="0.00")
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return WalletSchema(uuid=wallet.uuid,
                        balance=wallet.balance)

@router.get("/{wallet_id}",
            status_code=status.HTTP_200_OK)
async def get_wallet(wallet_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get wallet from UUID"""
    wallet = await db.get(Wallet, wallet_id)
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return {"balance": str(wallet.balance)}

@router.post("/{wallet_id}/operation",
            status_code=status.HTTP_200_OK,
            response_model=WalletSchema)
async def operate_wallet(wallet_id: UUID, wp: WalletOperation, db: AsyncSession = Depends(get_db)):
    """Operate wallet with deposit or withdraw."""
    try:
        wallet = await util.operate_wallet(
            session=db,
            wallet_id=wallet_id,
            operation=wp.operation_type,
            amount=wp.amount)
        return WalletSchema(uuid=wallet.uuid, balance=wallet.balance)
    except util.WalletNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except util.IncorrectOperation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
