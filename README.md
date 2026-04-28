# Shopping Mart Product Management System

A Python Tkinter + MongoDB project for managing shopping mart products, stock levels, product locations, prices, sold-out items, low-stock items, and high-demand products.

## Features

- Permanent Navi employee login protected with SHA-256 password hashes stored in MongoDB
- Full-screen employee access window with a single login panel
- Colorful dashboard focused on the item list, with separate windows for each action
- Product CRUD: view available items on the dashboard, then add, edit, sell, or delete through popup windows
- Track quantity, price, category, aisle, shelf, and sold count
- Record sales, automatically reducing stock
- Sold-out, low-stock, and high-demand filters
- Simple folder structure with backend files at the root and UI files in a separate `ui` folder

## Project Structure

```text
Shoppingmart/
  main.py
  requirements.txt
  README.md
  database.py
  models.py
  auth.py
  inventory.py
  ui/
    login_window.py
    dashboard_window.py
    styles.py
```

## Setup

1. Install MongoDB and make sure the MongoDB server is running.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

## Login

The app uses one permanent employee key:

- Username: `Navi`
- Password: `123navi`

The stored password is not plain text. It is saved as a SHA-256 hash in the `employees` collection.

## MongoDB Settings

By default, the app uses:

- URI: `mongodb://localhost:27017`
- Database: `shopping_mart_db`

## High Demand Logic

A product is shown as high demand when it has sold at least 10 units and either:

- sells at an average speed of 2 or more units per day, or
- has already reached its reorder level.
