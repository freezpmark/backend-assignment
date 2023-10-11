import logging
import random
import sys
from abc import ABC, abstractmethod
from functools import wraps
from pathlib import Path

src_path = Path(__file__).parents[1]
sys.path.append(str(src_path))
from app.models import DBCard
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

file_handler = logging.FileHandler("card.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def require_activation(method):
    """Validates whether the card is activated and ready to use."""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self.state, ActiveState):
            msg = f"{self.card_name_id} is going to perform {method.__name__}"
            logger.info(msg)
            return method(self, *args, **kwargs)
        else:
            msg = (
                "Cannot perform action because "
                f"{self.card_name_id} is not activated."
            )
            logger.error(msg)

    return wrapper


def generate_unique_name_id(id_num=1):
    while True:
        yield id_num
        id_num += 1


class Card(DBCard):
    card_nums = set()
    generator = generate_unique_name_id()

    def __init__(self, state: "CardState", account: "Account"):
        self.account = account
        self.card_id = next(self.generator)
        self.card_num = self._generate_unique_number()
        logger.info(
            "%s has been created. (%s)", self.card_name_id, self.card_num
        )
        self.set_state(state)

    def set_state(self, state: "CardState"):
        self.state = state
        self.state.card = self
        msg = (
            f"{self.card_name_id} has changed state to {type(state).__name__}"
        )
        logger.info(msg)

    @property
    def card_name_id(self):
        return "card" + str(self.card_id)

    def activate(self):
        self.state.activate_handle()

    def disable(self):
        self.state.disable_handle()

    @require_activation
    def withdraw(self, amount):
        if self.account.balance < amount:
            msg = "You do not have the amount you requested in your account!"
            logger.error(msg)
        else:
            self.account.sub_balance(amount)

    @require_activation
    def deposit(self, amount):
        self.account.add_balance(amount)

    @require_activation
    def check_balance(self):
        self.account.display_balance()

    @classmethod
    def _generate_unique_number(cls):
        while True:
            numbers = [str(random.randint(0, 9)) for _ in range(16)]
            card_num = "".join(numbers)
            if card_num not in cls.card_nums:
                cls.card_nums.add(card_num)
                return card_num


class CardState(ABC):
    @property
    def card(self):
        return self._card

    @card.setter
    def card(self, card):
        self._card = card

    @abstractmethod
    def activate_handle(self):
        pass

    @abstractmethod
    def disable_handle(self):
        pass


class ActiveState(CardState):
    def activate_handle(self):
        logger.error("%s is already active!", self.card.card_name_id)

    def disable_handle(self):
        logger.debug("Going to disable %s.", self.card.card_name_id)
        self.card.set_state(DisabledState())


class DisabledState(CardState):
    def activate_handle(self):
        logger.debug("Going to activate %s.", self.card.card_name_id)
        self.card.set_state(ActiveState())

    def disable_handle(self):
        logger.error("%s is already disabled!", self.card.card_name_id)
