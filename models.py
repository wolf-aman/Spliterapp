# models.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'email': self.email}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(data['name'], data['email'])

class Debt:
    def __init__(self, from_user: User, to_user: User, amount: float):
        self.from_user = from_user
        self.to_user = to_user
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.from_user.name} owes {self.to_user.name} ₹{self.amount:.2f}"

    @staticmethod
    def simplify(balances: Dict[str, float]) -> List[Dict[str, Any]]:
        debtors = {name: bal for name, bal in balances.items() if bal < -0.01}
        creditors = {name: bal for name, bal in balances.items() if bal > 0.01}
        
        simplified_debts = []
        while debtors and creditors:
            debtor_name, debtor_amount = list(debtors.items())[0]
            creditor_name, creditor_amount = list(creditors.items())[0]
            
            settle_amount = min(abs(debtor_amount), creditor_amount)
            simplified_debts.append({
                'from_user_name': debtor_name,
                'to_user_name': creditor_name,
                'amount': settle_amount
            })
            
            debtors[debtor_name] += settle_amount
            creditors[creditor_name] -= settle_amount
            
            if abs(debtors[debtor_name]) < 0.01: del debtors[debtor_name]
            if abs(creditors[creditor_name]) < 0.01: del creditors[creditor_name]
            
        return simplified_debts

class Split(ABC):
    def __init__(self, amount: float, participants: List[User]):
        self._amount = amount
        self._participants = participants

    @abstractmethod
    def calculate_shares(self) -> Dict[str, float]:
        pass

class EqualSplit(Split):
    def calculate_shares(self) -> Dict[str, float]:
        if not self._participants: return {}
        share = self._amount / len(self._participants)
        return {p.name: round(share, 2) for p in self._participants}

class PercentSplit(Split):
    def __init__(self, amount: float, participants: List[User], percentages: Dict[str, float]):
        super().__init__(amount, participants)
        if sum(percentages.values()) != 100:
            raise ValueError("Percentages must sum to 100.")
        self._percentages = percentages

    def calculate_shares(self) -> Dict[str, float]:
        return {p.name: round((self._amount * self._percentages[p.name]) / 100, 2) for p in self._participants}

class UnequalSplit(Split):
    def __init__(self, amount: float, participants: List[User], amounts: Dict[str, float]):
        super().__init__(amount, participants)
        if abs(sum(amounts.values()) - amount) > 0.01:
            raise ValueError("Sum of unequal shares must equal the total amount.")
        self._amounts = amounts

    def calculate_shares(self) -> Dict[str, float]:
        return self._amounts

class Expense:
    def __init__(self, description: str, amount: float, paid_by: User, participants: List[User], split_strategy: Split):
        self.description = description
        self.amount = amount
        self.paid_by = paid_by
        self.participants = participants
        self.split_strategy = split_strategy
        self._shares = self.split_strategy.calculate_shares()

class Group:
    def __init__(self, name: str):
        self.name = name
        self.members: List[User] = []
        self.expenses: List[Expense] = []
        self.settlements: List[Tuple[User, User, float]] = []
        self.debts: List[Debt] = []
    
    def add_member(self, user: User):
        if user not in self.members:
            self.members.append(user)

    def add_expense(self, expense: Expense):
        self.expenses.append(expense)
        self.simplify_debts()
    
    def settle_up(self, from_user: User, to_user: User, amount: float):
        self.settlements.append((from_user, to_user, amount))
        self.simplify_debts()

    def simplify_debts(self):
        balances = {member.name: 0.0 for member in self.members}

        for expense in self.expenses:
            balances[expense.paid_by.name] += expense.amount
            for user_name, share in expense._shares.items():
                if user_name in balances:
                    balances[user_name] -= share
        
        for from_user, to_user, amount in self.settlements:
            balances[from_user.name] += amount
            balances[to_user.name] -= amount

        simplified_debt_data = Debt.simplify(balances)
        
        self.debts.clear()
        user_map = {user.name: user for user in self.members}
        for debt_info in simplified_debt_data:
            from_user = user_map[debt_info['from_user_name']]
            to_user = user_map[debt_info['to_user_name']]
            self.debts.append(Debt(from_user, to_user, debt_info['amount']))
            
    def get_debts(self) -> List[Debt]:
        return self.debts