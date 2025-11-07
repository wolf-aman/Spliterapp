# SplitSmart

SplitSmart is a Python-based expense-sharing application that helps groups of people manage and settle shared expenses. It supports various splitting strategies, including equal, percentage-based, and unequal splits, and provides a user-friendly interface for managing users, groups, and expenses.

## Features

- **User Management**: Add and manage users with their names and email addresses.
- **Group Management**: Create groups, add members, and manage group expenses.
- **Expense Splitting**: Split expenses using different strategies:
  - Equal Split
  - Percentage Split
  - Unequal Split
- **Debt Simplification**: Automatically simplify debts between group members.
- **Data Persistence**: Save and load data to/from a JSON file.

## File Structure

- `models.py`: Contains the core classes for users, groups, expenses, and splitting strategies.
- `app.py`: Implements the main application logic, including user input handling and data persistence.
- `main.py`: Entry point for running the application.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Install required dependencies (if any)

### Running the Application

1. Clone the repository or download the files.
2. Navigate to the project directory.
3. Run the application:
   ```bash
   python main.py
   ```

### Usage

1. **Add Users**: Add users by providing their name and email.
2. **Create Groups**: Create a group and add members to it.
3. **Add Expenses**: Add expenses to a group, specifying the payer, participants, and splitting strategy.
4. **View Debts**: View outstanding debts for a group.
5. **Settle Up**: Record payments between members to settle debts.
6. **Save and Exit**: Save all data to a JSON file for future use.

## Example Workflow

1. Add users: Alice, Bob, and Charlie.
2. Create a group: "Trip to Goa" with Alice, Bob, and Charlie as members.
3. Add an expense: Alice paid ₹3000 for dinner, split equally among all members.
4. View debts: Bob and Charlie each owe Alice ₹1000.
5. Settle up: Bob pays Alice ₹1000.
6. Save and exit.

## Data Persistence

The application saves data to a JSON file (`splitsmart_data.json`) and loads it on startup. This ensures that all users, groups, and expenses are preserved between sessions.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the application.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Python Standard Library
- Inspiration from popular expense-sharing apps