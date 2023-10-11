import logging
import sys
import time
from functools import wraps
from pathlib import Path
from threading import Thread

src_path = Path(__file__).parents[1]
sys.path.append(str(src_path))
from app.card import ActiveState, Card
from app.models import DBAccount, DBBank

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

file_handler = logging.FileHandler("bank_account.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def timed_processing(method):
    """Simulates processing time for operation and ensures synchronization.

    With multiple registered cards, we might encounter unexpected results when two
    cards attempt to perform an action in the same time.
    The actions are: display_balance, add_balance, sub_balance
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        def operation():
            logger.debug("Going to sleep for two seconds.")
            time.sleep(2)
            logger.debug("Waking up.")
            method(self, *args, **kwargs)
            logger.info("Process <%s> is done", method.__name__)

        if not self.processing_thread or not self.processing_thread.is_alive():
            logger.info("Processing <%s>", method.__name__)
            self.processing_thread = Thread(target=operation)
            self.processing_thread.name = method.__name__
            self.processing_thread.start()
        else:
            msg = (
                f"Processing <{method.__name__}> has failed, "
                f"there's already <{self.processing_thread.name}> process ongoing!"
            )
            logger.error(msg)
            return

    return wrapper


class Bank(DBBank):
    def __init__(self, name):
        self.name = name
        self.accounts = []
        logger.info("%s bank has been created.", name)

    def create_account(self, name, email, withdraw_notify_limit):
        new_account = Account(name, email, withdraw_notify_limit)
        self.accounts.append(new_account)
        logger.info("Account with %s email has been created.", email)

        return new_account


class Account(DBAccount):
    def __init__(self, name, email, withdraw_notify_limit):
        self.name = name
        self.email = email
        # self.cards = []
        self._balance = 0
        self.withdrawed = 0
        self.withdraw_notify_limit = withdraw_notify_limit

        self.processing_thread = None

    def register_cards(self, amount: int=1):
        if 1 < amount > 5:
            logger.error("You can only register 1-5 cards at a time!")
            return
        for _ in range(amount):
            Card(ActiveState(), self)

    @property
    def balance(self):
        return self._balance

    @timed_processing
    def display_balance(self):
        print(f"{self.balance}$")

    @timed_processing
    def add_balance(self, amount):
        self._balance += amount

    @timed_processing
    def sub_balance(self, amount):
        self._balance -= amount
        self.withdrawed += amount
        if self.withdrawed > self.withdraw_notify_limit:
            logger.warning("You've have surpassed withdrawal limit!")


if __name__ == "__main__":
    bank = Bank("Bering Bank")      # INFO:Bering Bank bank has been created.
    account = bank.create_account(
        "Peter", "pmark@azet.sk", withdraw_notify_limit=50
    )                               # INFO:Account with pmark@azet.sk email has been created.
    account.register_cards(3)       # INFO:card has been created ...
    print(len(account.cards))

    card1 = account.cards[0]
    card2 = account.cards[1]
    card1.deposit(200)      # INFO:card1 is going to perform deposit
                            # INFO:Processing <add_balance>
    card2.deposit(300)      # INFO:card2 is going to perform deposit
                            # ERROR:Processing <add_balance> has failed, there's already <add_balance> process ongoing!
    card2.check_balance()   # INFO:card2 is going to perform check_balance
                            # ERROR:Processing <display_balance> has failed, there's already <add_balance> process ongoing!

    card1.activate()    # ERROR:card1 is already active!
    card1.disable()     # INFO:card1 has changed state to DisabledState
    card2.disable()     # INFO:card2 has changed state to DisabledState
    card1.activate()    # INFO:card1 has changed state to ActiveState
    card1.disable()     # INFO:card1 has changed state to DisabledState
    card1.disable()     # ERROR:card1 is already disabled!
    card1.activate()    # INFO:card1 has changed state to ActiveState

    # INFO:Process <add_balance> is done
    time.sleep(3)       
    card2.withdraw(500) # ERROR:Cannot perform action because card2 is not activated
    card2.activate()    # INFO:card2 has changed state to ActiveState
    card2.withdraw(500) # INFO:card2 is going to perform withdraw
                        # ERROR:You do not have the amount you requested in your account!
    card2.withdraw(75)  # INFO:card2 is going to perform withdraw
                        # INFO:Processing <sub_balance>
                        # WARNING:You've have surpassed withdrawal limit!
    # INFO:Process <sub_balance> is done
    time.sleep(3)
    card1.check_balance()   # INFO:card1 is going to perform check_balance
                            # INFO:Processing <display_balance>
    # 125$
    # INFO:Process <display_balance> is done
