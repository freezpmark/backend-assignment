import sys
import time
from pathlib import Path

import pytest

src_path = Path(__file__).parents[2]
sys.path.append(str(src_path))
from app.bank_account import Account, Bank
from app.card import ActiveState, Card, DisabledState


def account_factory():
    """
    Helper function to create account
    """
    bank = Bank("Bering Bank")
    name = "Peter"
    email = "pmark@azet.sk"
    withdraw_notify_limit = 50
    account = bank.create_account(name, email, withdraw_notify_limit)

    return account


def card_factory(account_id):
    """
    Helper function to register card to a user
    """

    account_id.register_cards()

    return account_id.cards[0]


@pytest.mark.asyncio
async def test_create_user_account():
    """
    Test Account Creating Logic
    """

    # GIVEN
    bank = Bank("Bering Bank")
    name = "Peter"
    email = "pmark@azet.sk"
    withdraw_notify_limit = 50

    # WHEN
    account = bank.create_account(name, email, withdraw_notify_limit)

    # THEN
    assert account is not None
    assert account.name == name
    assert account.email == email
    assert account.withdraw_notify_limit == withdraw_notify_limit
    assert account.balance == 0
    assert len(account.cards) == 0


@pytest.mark.asyncio
async def test_register_cards():

    # GIVEN
    _account = account_factory()
    card_amount = 3

    # WHEN
    _account.register_cards(card_amount)
    _account.register_cards()
    card_number = _account.cards[0].card_num

    # THEN
    assert len(_account.cards) == card_amount + 1  # multiple cards register
    assert _account.cards[0].account == _account  # card association with acc
    assert len(card_number) == 16  # length
    assert any(char.isdigit() for char in card_number)  # only nums
    assert len(set(_account.cards)) == card_amount + 1  # uniqueness


@pytest.mark.asyncio
async def test_disable_card():

    # GIVEN
    _account = account_factory()
    _card = card_factory(account_id=_account)

    # WHEN
    _card.disable()

    # THEN
    assert isinstance(_card.state, DisabledState)
    assert not isinstance(_card.state, ActiveState)


@pytest.mark.asyncio
async def test_enable_card():

    # GIVEN
    _account = account_factory()
    _card = card_factory(account_id=_account)

    # WHEN
    # assert isinstance(_card.state, ActiveState)
    _card.disable()
    # assert not isinstance(_card.state, DisabledState)
    _card.activate()

    # THEN
    assert isinstance(_card.state, ActiveState)
    assert not isinstance(_card.state, DisabledState)


@pytest.mark.asyncio
async def test_deposit_cash():

    # GIVEN
    _account = account_factory()
    _card = card_factory(account_id=_account)

    # WHEN
    _card.deposit(200)
    _card.deposit(50)
    time.sleep(3)
    _card.deposit(100)
    time.sleep(3)

    # THEN
    assert _account.balance == 300


@pytest.mark.asyncio
async def test_withdraw_cash():

    # GIVEN
    _account = account_factory()
    _card = card_factory(account_id=_account)

    # WHEN
    _card.deposit(400)
    time.sleep(3)
    _card.withdraw(450)
    _card.withdraw(350)
    time.sleep(3)

    # THEN
    assert _account.balance == 50


@pytest.mark.asyncio
async def test_check_account_balance():

    # GIVEN
    _account = account_factory()
    _card = card_factory(account_id=_account)

    # WHEN
    _card.deposit(200)
    time.sleep(3)
    displayed_balance = _card.check_balance()
    displayed_balance = _account.balance
    time.sleep(3)

    # THEN
    assert displayed_balance == 200
