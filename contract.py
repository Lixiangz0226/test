"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ A new month has begun corresponding to <month> and <year>.
        This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ A contract for a phone line

    This is a subclass of Contract

    === Public Attributes ===
    start:
        starting date for the contract
    end:
        the end date for the contract
    """
    end: datetime.date
    current_month: int
    current_year: int

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        Contract.__init__(self, start)
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.current_month = month
        self.current_year = year

        if month == self.start.month and year == self.start.year:
            self.bill = bill
            self.bill.add_fixed_cost(TERM_DEPOSIT)
        else:
            self.bill = bill

        self.bill.set_rates("TERM", TERM_MINS_COST)
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)

    def bill_call(self, call: Call) -> None:
        call_minutes = ceil(call.duration / 60.0)
        used_free_minutes = self.bill.free_min

        free_minutes_remaining = 100 - used_free_minutes

        if free_minutes_remaining > call_minutes:
            self.bill.add_free_minutes(call_minutes)
        elif free_minutes_remaining > 0:
            self.bill.add_free_minutes(free_minutes_remaining)
            self.bill.add_billed_minutes(call_minutes - free_minutes_remaining)
        else:
            self.bill.add_billed_minutes(call_minutes)


class MTMContract(Contract):
    """ A contract for a phone line

    This is a subclass of Contract

    === Public Attributes ===
    start:
        starting date for the contract
    """
    def __init__(self, start: datetime.date) -> None:
        Contract.__init__(self, start)
        self.new_month(start.month, start.year, Bill())

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        bill.set_rates("MTM", MTM_MINS_COST)
        bill.add_fixed_cost(MTM_MONTHLY_FEE)


class PrepaidContract(Contract):
    """ A contract for a phone line

    This is a subclass of Contract

    === Public Attributes ===
    start:
        starting date for the contract
    balance:
        the money the costumer needs to pay

    ===Private Attributes===
    balance:
        amount of money the customer owes.
        if the balance is negative, this indicates
        the customer has this much credit for prepaying the bill.
    """
    balance: float

    def __init__(self, start: datetime.date, balance: int) -> None:
        Contract.__init__(self, start)
        self.balance = -balance
        self.new_month(start.month, start.year, Bill())

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill.add_fixed_cost(self.balance)

    def bill_call(self, call: Call) -> None:
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))
        cost_to_balance = self.bill.get_cost()
        self.balance = cost_to_balance
        self.bill.add_fixed_cost(-cost_to_balance)

        if self.balance > -10:
            self.balance = self.balance - 25

        self.bill.add_fixed_cost(self.balance)

    def cancel_contract(self) -> float:
        self.start = None

        if self.bill.get_cost() > 0:
            return self.bill.get_cost()
        else:
            return 0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
