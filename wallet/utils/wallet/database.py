from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from wallet.db.models import Wallet

class WalletNotFound(Exception):
    pass

class IncorrectOperation(Exception):
    pass

async def operate_wallet(
        session: AsyncSession,
        wallet_id: UUID,
        operation: str,
        amount: float
):
    if operation == "DEPOSIT":
        state = (
            update(Wallet)
            .where(Wallet.uuid == wallet_id)
            .values(balance=Wallet.balance + amount)
            .returning(Wallet)
        )
        result = await session.execute(state)
        wallet = result.scalar()
        if not wallet:
            raise WalletNotFound
    elif operation == "WITHDRAW":
        state = (
            update(Wallet)
            .where(Wallet.uuid == wallet_id, Wallet.balance >= amount)
            .values(balance=Wallet.balance - amount)
            .returning(Wallet)
        )
        result = await session.execute(state)
        wallet = result.scalar_one_or_none()
        if not wallet:
            exist = await session.execute(
                select(Wallet).where(Wallet.uuid == wallet_id)
            )
            if not exist:
                raise WalletNotFound
            else:
                raise IncorrectOperation
    await session.commit()
    return wallet
