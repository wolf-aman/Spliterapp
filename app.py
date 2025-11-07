# app.py

import json
import os
from functools import wraps
from models import User, Group, Expense, EqualSplit, PercentSplit, UnequalSplit

def find_group(func):
    """Decorator to find a group and handle 'not found' errors."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        group_name = input("Enter group name: ").strip()
        group = self.groups.get(group_name)
        if not group:
            print("Error: Group not found.")
            return
        
        return func(self, group, *args, **kwargs)
    return wrapper

class SplitSmartApp:
    def __init__(self, data_file='splitsmart_data.json'):
        self.users = {}
        self.groups = {}
        self.data_file = data_file
        self.load_data()

    def run(self):
        menu = {
            '1': ("Add User", self._add_user),
            '2': ("Create Group", self._create_group),
            '3': ("Add Expense to Group", self._add_expense),
            '4': ("View Group Debts", self._view_debts),
            '5': ("Settle Up in Group", self._settle_up),
            '6': ("Save Data and Exit", self._save_and_exit),
        }
        while True:
            print("\n" + "="*15 + " SplitSmart Menu " + "="*15)
            for key, (desc, _) in menu.items():
                print(f"{key}. {desc}")
            print("="*47)
            
            choice = input("Enter your choice: ")
            if choice in menu:
                _, action = menu[choice]
                action()
                if choice == '6':
                    break
            else:
                print("Invalid choice. Please try again.")

    def _add_user(self):
        name = input("Enter user name: ").strip()
        if name in self.users:
            print("Error: User already exists.")
            return
        email = input("Enter user email: ").strip()
        self.users[name] = User(name, email)
        print(f"User '{name}' added successfully!")

    def _create_group(self):
        group_name = input("Enter group name: ").strip()
        if group_name in self.groups:
            print("Error: Group already exists.")
            return
        group = Group(group_name)
        member_names_str = input("Add members by name (comma-separated): ").strip()
        member_names = [n.strip() for n in member_names_str.split(',')]
        for name in member_names:
            user = self.users.get(name)
            if user:
                group.add_member(user)
            else:
                print(f"Warning: User '{name}' not found and not added.")
        self.groups[group_name] = group
        print(f"Group '{group_name}' created!")

    @find_group
    def _view_debts(self, group: Group):
        print(f"\n--- Debts for {group.name} ---")
        debts = group.get_debts()
        if not debts:
            print("No outstanding debts.")
        else:
            for debt in debts:
                print(debt)
        print("------------------------")
    
    @find_group
    def _settle_up(self, group: Group):
        from_name = input("Who paid? ").strip()
        to_name = input("Who received? ").strip()
        from_user, to_user = self.users.get(from_name), self.users.get(to_name)
        
        if not from_user or not to_user:
            print("Error: One or both users not found.")
            return
        
        try:
            amount = float(input("Enter amount: "))
            group.settle_up(from_user, to_user, amount)
            self._view_debts_for_group(group)
        except ValueError:
            print("Invalid amount.")

    @find_group
    def _add_expense(self, group: Group):
        try:
            description = input("Description: ")
            amount = float(input("Amount: "))
            payer_name = input("Paid by: ").strip()
            payer = self.users.get(payer_name)
            
            if not payer or payer not in group.members:
                print("Error: Payer not valid or not in the group.")
                return

            participants_str = input("Participants (comma-separated, or 'all'): ")
            participants = group.members if participants_str.lower() == 'all' else \
                           [self.users[n.strip()] for n in participants_str.split(',') if n.strip() in self.users]

            if not participants:
                print("No valid participants found for this expense.")
                return

            split_type = input("Split type (equal, percent, unequal): ").lower()
            split_obj = self._get_split_strategy(split_type, amount, participants)
            
            if split_obj:
                expense = Expense(description, amount, payer, participants, split_obj)
                group.add_expense(expense)
                self._view_debts_for_group(group)

        except (ValueError, KeyError) as e:
            print(f"Error creating expense: {e}")

    def _get_split_strategy(self, split_type, amount, participants):
        if split_type == 'equal':
            return EqualSplit(amount, participants)
        elif split_type == 'percent':
            percentages = {p.name: float(input(f"% for {p.name}: ")) for p in participants}
            return PercentSplit(amount, participants, percentages)
        elif split_type == 'unequal':
            amounts = {p.name: float(input(f"Amount for {p.name}: ")) for p in participants}
            return UnequalSplit(amount, participants, amounts)
        else:
            print("Invalid split type.")
            return None
    
    def _view_debts_for_group(self, group: Group):
        # Helper to avoid asking for group name again after an action
        print(f"\n--- Updated Debts for {group.name} ---")
        for debt in group.get_debts() or ["No outstanding debts."]:
            print(debt)
        print("---------------------------------")
        
    def _save_and_exit(self):
        data = {
            'users': [user.to_dict() for user in self.users.values()],
            'groups': [self._group_to_dict(group) for group in self.groups.values()]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {self.data_file}. Exiting.")

    def _group_to_dict(self, group: Group) -> dict:
        return {
            'name': group.name,
            'members': [member.name for member in group.members],
            'expenses': [{
                'description': exp.description, 'amount': exp.amount, 
                'paid_by': exp.paid_by.name, 'participants': [p.name for p in exp.participants],
                'shares': exp._shares
            } for exp in group.expenses],
            'settlements': [
                {'from': s[0].name, 'to': s[1].name, 'amount': s[2]} for s in group.settlements
            ]
        }

    def load_data(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            return

        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            self.users = {u['name']: User.from_dict(u) for u in data['users']}
            for g_data in data.get('groups', []):
                group = Group(g_data['name'])
                group.members = [self.users[name] for name in g_data.get('members', [])]
                
                for e_data in g_data.get('expenses', []):
                    payer = self.users[e_data['paid_by']]
                    participants = [self.users[name] for name in e_data['participants']]
                    split_obj = UnequalSplit(e_data['amount'], participants, e_data['shares'])
                    expense = Expense(e_data['description'], e_data['amount'], payer, participants, split_obj)
                    group.expenses.append(expense)
                
                for s_data in g_data.get('settlements', []):
                    from_user = self.users[s_data['from']]
                    to_user = self.users[s_data['to']]
                    group.settlements.append((from_user, to_user, s_data['amount']))
                
                group.simplify_debts()
                self.groups[group.name] = group
            print(f"Data successfully loaded from {self.data_file}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading data: {e}. Starting fresh.")