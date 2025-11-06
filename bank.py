class NegativeAmountError(Exception):
    pass
class InsufficientFundsError(Exception):
    pass
class LoanOverpaymentError(Exception): 
    pass

class Account:
    def __init__(self, num, owner = None):
        self.account_number, self.owner, self.balance = num, owner, 0.0

    def deposit(self, amount):
        if amount < 0: raise NegativeAmountError
        self.balance += amount

    def withdraw(self, amount):
        if amount < 0: raise NegativeAmountError
        if amount > self.balance: raise InsufficientFundsError
        self.balance -= amount

    def __str__(self): 
        return f"Account №{self.account_number}, баланс: {self.balance:.2f}"


class CheckingAccount(Account): 
    pass

class SavingsAccount(Account):
    def __init__(self, num, rate, owner = None):
        super().__init__(num, owner); self.interest_rate_percent = rate
    def add_interest(self): 
        self.balance += self.balance * self.interest_rate_percent / 100
    def __str__(self): 
        return f"SavingsAccount №{self.account_number}, баланс: {self.balance:.2f}, ставка: {self.interest_rate_percent}%"


class Loan:
    def __init__(self, amount, months, rate, borrower = None):
        if amount <= 0 or months <= 0: raise ValueError
        self.amount, self.months, self.rate, self.remaining_debt, self.borrower = amount, months, rate, amount, borrower

    def monthly_interest_rate(self):
        return self.rate / 12 / 100
    def calculate_monthly_payment(self): 
        return self.amount / self.months + self.amount * self.rate / 100 / 12
    def make_payment(self, amount):
        if amount < 0: raise NegativeAmountError
        if amount > self.remaining_debt: raise LoanOverpaymentError
        self.remaining_debt = amount
    def __str__(self): 
        return f"Loan {self.amount}, {self.rate}%, остаток {self.remaining_debt:.2f}"

class ConsumerLoan(Loan):
    def __init__(self, amount, months, borrower = None): 
        super().__init__(amount, months, 15, borrower)

class AutoLoan(Loan):
    def __init__(self, amount, months, car, borrower = None):
        super().__init__(amount, months, 10, borrower); self.car_model = car
    def __str__(self): 
        return super().__str__() + f", авто: {self.car_model}"


class MortgageLoan(Loan):
    def __init__(self, amount, months, prop_value, borrower = None):
        super().__init__(amount, months, 7, borrower); self.property_value = prop_value
    def __str__(self): 
        return super().__str__() + f", недвижимость: {self.property_value}"


class Customer:
    def __init__(self, name, age):
        self.name, self.age, self.accounts, self.loans = name, age, [], []

    def open_account(self, acc): 
        acc.owner = self; self.accounts.append(acc)
    def take_loan(self, loan): 
        loan.borrower = self; self.loans.append(loan)
    def get_total_balance(self): 
        return sum(a.balance for a in self.accounts)
    def __str__(self): 
        return f"Customer {self.name} ({self.age}), счетов: {len(self.accounts)}, кредитов: {len(self.loans)}"


class Bank:
    def __init__(self, name): 
        self.name, self.customers = name, []
    def add_customer(self, c): 
        self.customers.append(c)
    def find_customer(self, name): 
        return next((x for x in self.customers if x.name == name), None)
    def transfer(self, from_acc, to_acc, amount):
        if amount < 0: raise NegativeAmountError
        if from_acc.balance < amount: raise InsufficientFundsError
        from_acc.withdraw(amount); to_acc.deposit(amount)
    def show_all_customers(self):
        if not self.customers: return "Нет клиентов"
        return "\n".join([f"{self.name}:" + "\n".join(str(c) for c in self.customers)])


# Пример
if __name__ == "__main__":
    bank = Bank("OpenAI Bank")
    alice = Customer("Alice", 28)
    acc1 = CheckingAccount("001"); acc1.deposit(5000); alice.open_account(acc1)
    sav = SavingsAccount("S001", 3); sav.deposit(1000); alice.open_account(sav)
    loan = MortgageLoan(100000, 24, 120000); alice.take_loan(loan)
    bank.add_customer(alice)

    print(bank.show_all_customers())
    print("Общий баланс:", alice.get_total_balance())
    print("Кредит:", loan)