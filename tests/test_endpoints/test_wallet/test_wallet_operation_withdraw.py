import os
import pytest
import asyncio
from starlette import status

async def test_wallet_operation_withdraw(test_client, test_wallet, get_url):
    response = await test_client.post(f"{get_url}/{test_wallet.uuid}/operation",
                                      json={"operation_type": "WITHDRAW",
                                            "amount": 25})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['uuid'] == str(test_wallet.uuid)
    assert response.json()['balance'] == '100.00'

async def test_wallet_operation_withdraw_over_balance(test_client, test_wallet, get_url):
    response = await test_client.post(f"{get_url}/{test_wallet.uuid}/operation",
                                      json={"operation_type": "WITHDRAW",
                                            "amount": 500})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

async def test_concurrent_wallet_withdraw(test_client, test_wallet,get_url):
    async def deposit_once(amount):
        response = await test_client.post(f"{get_url}/{test_wallet.uuid}/operation",
                                          json={'operation_type': 'WITHDRAW',
                                                'amount': amount})
        return response
    tasks = [deposit_once(5) for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        assert response.status_code == status.HTTP_200_OK
    result = await test_client.get(f"{get_url}/{test_wallet.uuid}")
    assert result.json()["balance"] == "100.00"