import psycopg2
from pathlib import Path
import pandas as pd


def load_csv(path: str):
    # skipinitialspace removes extra spaces after the delimiter, keep_default_na=False prevents empty strings from being converted to NaN
    return pd.read_csv(path, skipinitialspace=True, keep_default_na=False)


def main():
    host = "postgres"
    database = "postgres"
    user = "postgres"
    pas = "postgres"
    conn = psycopg2.connect(host=host, database=database, user=user, password=pas)
    cur = conn.cursor()

    base_dir = Path("/app/data")
    # Table creation queries
    accounts_query = """
        CREATE TABLE IF NOT EXISTS accounts (
            customer_id INT PRIMARY KEY,
            first_name VARCHAR(25),
            last_name VARCHAR(25),
            address_1 VARCHAR(100),
            address_2 VARCHAR(100),
            city VARCHAR(25),
            state VARCHAR(25),
            zip_code INT,
            join_date DATE
        );
    """

    products_query = """
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            product_code VARCHAR(25),
            product_description VARCHAR(100)
        );
    """

    transactions_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id VARCHAR(50) PRIMARY KEY,
            transaction_date DATE,
            product_id INT,
            product_code VARCHAR(25),
            product_description VARCHAR(100),
            quantity INT,
            account_id INT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (account_id) REFERENCES accounts(customer_id)
        );
    """
    # Index creation queries
    product_trans_index_query = "CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions (product_id);"
    account_trans_index_query = "CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions (account_id);"
    # Execution
    cur.execute(accounts_query)
    cur.execute(products_query)
    cur.execute(transactions_query)
    cur.execute(product_trans_index_query)
    cur.execute(account_trans_index_query)
    # Loading data using pandas
    accounts_df = load_csv(str(base_dir / "accounts.csv"))
    products_df = load_csv(str(base_dir / "products.csv"))
    transactions_df = load_csv(str(base_dir / "transactions.csv"))
    # Update date formats to match PostgreSQL's expected format
    accounts_df["join_date"] = pd.to_datetime(accounts_df["join_date"], format="%Y/%m/%d").dt.strftime("%Y-%m-%d")
    transactions_df["transaction_date"] = pd.to_datetime(transactions_df["transaction_date"], format="%Y/%m/%d").dt.strftime("%Y-%m-%d")
    # Insert data into tables using executemany for batch insertion
    accounts_insert_query = """
        INSERT INTO accounts (customer_id, first_name, last_name, address_1, address_2, city, state, zip_code, join_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    products_insert_query = """
        INSERT INTO products (product_id, product_code, product_description)
        VALUES (%s, %s, %s)
    """
    transactions_insert_query = """
        INSERT INTO transactions (transaction_id, transaction_date, product_id, product_code, product_description, quantity, account_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    # Insert data into tables using executemany for batch insertion
    cur.executemany(
        accounts_insert_query,
        [tuple(row) for row in accounts_df.itertuples(index=False, name=None)]
    )
    cur.executemany(
        products_insert_query,
        [tuple(row) for row in products_df.itertuples(index=False, name=None)]
    )
    cur.executemany(
        transactions_insert_query,
        [tuple(row) for row in transactions_df.itertuples(index=False, name=None)]
    )
    # Commit the changes to the database
    conn.commit()

    cur.execute("SELECT customer_id, first_name, last_name FROM accounts ORDER BY customer_id;")
    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
