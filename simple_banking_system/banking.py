import random
from typing import Optional, Tuple, List
from enum import Enum
import sqlite3


class Bank(object):
    def __init__(self, bank_iin: int, database: sqlite3.Connection) -> None:
        self.bank_iin = bank_iin
        self.database = database
        self.cur: sqlite3.Cursor = self.database.cursor()

        create_table = """
            CREATE TABLE IF NOT EXISTS card (
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0);
        """

        self.cur.execute(create_table)
        self.database.commit()

    def create_account(self) -> Tuple['BankAccount', str]:
        account_number = random.randint(0, 999999999)

        self.cur.execute(f"""
            SELECT * FROM card WHERE id = {account_number};
        """)
        while self.cur.fetchall():
            account_number = random.randint(0, 999999999)
            self.cur.execute(f"""
                SELECT * FROM card WHERE id = {account_number};          
            """)

        new_account = BankAccount(account_number, self, 0)
        card_number = new_account.get_card_number()
        pin = f"{random.randint(0, 9999):04d}"

        self.cur.execute(f"""
            INSERT 
                INTO card (id, number, pin) 
                VALUES ({account_number}, '{card_number}', '{pin}');
        """)
        self.database.commit()

        return new_account, pin

    def get_account(self, card_number: str,
                    pin: str) -> Optional['BankAccount']:
        try:
            account_number = int(card_number[6:15])
            self.cur.execute(f"""
                SELECT * FROM card WHERE id = {account_number};
            """)
            table_row = self.cur.fetchone()

            if table_row[2] == pin:
                return BankAccount(account_number, self, table_row[3])
            else:
                return None
        except (ValueError, TypeError):
            return None

    def add_funds(self, account: 'BankAccount',
                  income: float) -> 'BankAccount':
        new_balance = account.balance + income

        self.cur.execute(f"""
            UPDATE card 
                SET balance = {new_balance} 
                WHERE id = {account.account_number};
        """)
        self.database.commit()

        account.balance = new_balance
        return account

    def close_account(self, account: 'BankAccount') -> None:
        self.cur.execute(f"""
            DELETE FROM card WHERE id = {account.account_number};
        """)
        self.database.commit()

    @staticmethod
    def luhn_card_verification(destination_card: str) -> bool:
        card_number: str = destination_card[:15]
        card_digits: List[int] = [int(dig) for dig in card_number]
        card_digits = [dig if ind % 2 else dig * 2
                       for ind, dig in enumerate(card_digits)]
        sum_of_digits = sum([dig - 9 if dig > 9 else dig
                             for dig in card_digits])
        return \
            destination_card[:15] + str((10 - sum_of_digits % 10) % 10) \
            == destination_card

    def is_card_exists(self, destination_card: str) -> bool:
        try:
            account_number = int(destination_card[6:15])

            self.cur.execute(f"""
                SELECT * FROM card WHERE id = {account_number};
            """)
            table_row = self.cur.fetchone()

            if table_row[0] == account_number:
                return True
            else:
                return False
        except (ValueError, TypeError):
            return False

    def transfer_funds(self, account: 'BankAccount',
                       destination_card: str,
                       amount: float) -> 'BankAccount':
        new_balance = account.balance - amount

        destination_account = int(destination_card[6:15])
        self.cur.execute(f"""
            SELECT id, balance 
                FROM card 
                WHERE id = {destination_account};
        """)
        new_destination_balance = self.cur.fetchone()[1] + amount

        self.cur.execute(f"""
            UPDATE card 
                SET balance = {new_destination_balance} 
                WHERE id = {destination_account};
        """)
        self.cur.execute(f"""
            UPDATE card 
                SET balance = {new_balance} 
                WHERE id = {account.account_number};
        """)
        self.database.commit()

        account.balance = new_balance
        return account


class MenuLevel(Enum):
    TOP = 1
    ACCOUNT = 2


class TopMenu(Enum):
    CREATE = 1
    LOGIN = 2
    EXIT = 0


class AccountMenu(Enum):
    BALANCE = 1
    INCOME = 2
    TRANSFER = 3
    CLOSE = 4
    LOGOUT = 5
    EXIT = 0


class ConsoleUI(object):
    def __init__(self) -> None:
        self.level: MenuLevel = MenuLevel.TOP

    def display_menu(self) -> None:
        if self.level == MenuLevel.ACCOUNT:
            print()
            print(f"{AccountMenu.BALANCE.value}. Balance")
            print(f"{AccountMenu.INCOME.value}. Add income")
            print(f"{AccountMenu.TRANSFER.value}. Do transfer")
            print(f"{AccountMenu.CLOSE.value}. Close account")
            print(f"{AccountMenu.LOGOUT.value}. Log out")
            print(f"{AccountMenu.EXIT.value}. Exit")
        else:
            print()
            print(f"{TopMenu.CREATE.value}. Create an account")

            print(f"{TopMenu.LOGIN.value}. Log into account")
            print(f"{TopMenu.EXIT.value}. Exit")

    @staticmethod
    def message_show_new_card(card_number: str, pin: str) -> None:
        print("\nYour card has been created")
        print("Your card number:")
        print(card_number)
        print("PIN:")
        print(pin)

    @staticmethod
    def message_exit_warning() -> None:
        print("\nBye!")

    @staticmethod
    def message_wrong_command() -> None:
        print("\nTry again...")

    @staticmethod
    def message_enter_card() -> None:
        print("\nEnter your card number:")

    @staticmethod
    def message_enter_pin() -> None:
        print("Enter your PIN:")

    @staticmethod
    def message_login_success() -> None:
        print("\nYou have successfully logged in!")

    @staticmethod
    def message_login_failed() -> None:
        print("\nWrong card number or PIN!")

    @staticmethod
    def message_logout_success() -> None:
        print("\nYou have successfully logged out!")

    @staticmethod
    def message_show_balance(balance: float) -> None:
        print(f"\nBalance: {balance}")

    @staticmethod
    def message_no_money() -> None:
        print("Not enough money!")

    @staticmethod
    def message_same_account() -> None:
        print("\nYou can't transfer money to the same account!")

    @staticmethod
    def message_wrong_card_number() -> None:
        print("\nProbably you made a mistake in the card number. "
              "Please try again!")

    @staticmethod
    def message_no_card() -> None:
        print("Such a card does not exist.")

    @staticmethod
    def message_income_added() -> None:
        print("Income was added!")

    @staticmethod
    def message_transfer_success() -> None:
        print("\nSuccess!")

    @staticmethod
    def message_account_closed() -> None:
        print("\nThe account has been closed!")

    @staticmethod
    def message_not_implemented() -> None:
        print("\nSorry, this function is not yet implemented!")

    @staticmethod
    def message_enter_income() -> None:
        print("\nEnter income:")

    @staticmethod
    def message_enter_card_for_transfer() -> None:
        print("\nTransfer"
              "\nEnter card number:")

    @staticmethod
    def message_enter_amount_for_transfer() -> None:
        print("Enter how much money you want to transfer:")


class Controller(object):
    def __init__(self, ui: ConsoleUI, bank: Bank) -> None:
        self.ui: ConsoleUI = ui
        self.bank: Bank = bank
        self.account: Optional[BankAccount] = None

    def loop(self) -> None:
        while True:
            self.ui.display_menu()
            self.process_user_input(input(">"))

    def process_user_input(self, user_input: str) -> None:
        actions = {
            (MenuLevel.TOP, str(TopMenu.CREATE.value)):
                self.handler_create_account,
            (MenuLevel.TOP, str(TopMenu.LOGIN.value)):
                self.handler_login,
            (MenuLevel.TOP, str(TopMenu.EXIT.value)):
                self.handler_exit,
            (MenuLevel.ACCOUNT, str(AccountMenu.BALANCE.value)):
                self.handler_balance,
            (MenuLevel.ACCOUNT, str(AccountMenu.LOGOUT.value)):
                self.handler_logout,
            (MenuLevel.ACCOUNT, str(AccountMenu.EXIT.value)):
                self.handler_exit,
            (MenuLevel.ACCOUNT, str(AccountMenu.INCOME.value)):
                self.handler_income,
            (MenuLevel.ACCOUNT, str(AccountMenu.TRANSFER.value)):
                self.handler_transfer,
            (MenuLevel.ACCOUNT, str(AccountMenu.CLOSE.value)):
                self.handler_close_account,
        }

        try:
            actions[(self.ui.level, user_input)]()
        except KeyError:
            self.ui.message_wrong_command()

    def handler_income(self) -> None:
        self.ui.message_enter_income()
        try:
            self.account = self.bank.add_funds(self.account, float(input()))
            self.ui.message_income_added()
        except ValueError:
            self.ui.message_wrong_command()

    def handler_transfer(self) -> None:
        self.ui.message_enter_card_for_transfer()
        destination_card = input()

        if not self.bank.luhn_card_verification(destination_card):
            self.ui.message_wrong_card_number()
        elif not self.bank.is_card_exists(destination_card):
            self.ui.message_no_card()
        else:
            self.ui.message_enter_amount_for_transfer()
            amount = float(input())
            if amount > self.account.balance:
                self.ui.message_no_money()
            else:
                self.account = self.bank.transfer_funds(self.account,
                                                        destination_card,
                                                        amount)
                self.ui.message_transfer_success()

    def handler_close_account(self) -> None:
        self.bank.close_account(self.account)
        self.ui.level = MenuLevel.TOP
        self.ui.message_account_closed()

    def handler_create_account(self) -> None:
        user_account, pin = self.bank.create_account()
        self.ui.message_show_new_card(user_account.get_card_number(), pin)

    def handler_login(self) -> None:
        self.ui.message_enter_card()
        user_card = input()
        self.ui.message_enter_pin()
        user_pin = input()
        user_account = self.bank.get_account(user_card, user_pin)

        if user_account:
            self.account = user_account
            self.ui.level = MenuLevel.ACCOUNT
            self.ui.message_login_success()
        else:
            self.ui.message_login_failed()

    def handler_balance(self) -> None:
        self.ui.message_show_balance(self.account.balance)

    def handler_logout(self) -> None:
        self.ui.level = MenuLevel.TOP
        self.ui.message_logout_success()

    def handler_exit(self) -> None:
        self.ui.message_exit_warning()
        exit()


class BankAccount(object):
    def __init__(self, account_number: int,
                 account_bank: Bank, balance: float) -> None:
        self.account_number = account_number
        self.bank_iin = account_bank.bank_iin
        self.balance = balance

    def get_luhn_ending(self) -> str:
        card_number: str = f"{self.bank_iin}" \
                      f"{self.account_number:09d}"
        card_digits: List[int] = [int(dig) for dig in card_number]
        card_digits = [dig if ind % 2 else dig * 2
                       for ind, dig in enumerate(card_digits)]
        sum_of_digits = sum([dig - 9 if dig > 9 else dig
                             for dig in card_digits])
        return str((10 - sum_of_digits % 10) % 10)

    def get_card_number(self) -> str:
        return f"{self.bank_iin}" \
               f"{self.account_number:09d}" \
               f"{self.get_luhn_ending()}"


def main() -> None:
    bank = Bank(400000, sqlite3.connect('card.s3db'))
    console = ConsoleUI()

    controller = Controller(console, bank)
    controller.loop()


if __name__ == "__main__":
    main()
