import pymysql.cursors
import os
import hashlib
import logging
import time
from functools import wraps

class Database:
    MAX_RETRIES = 5
    RETRY_DELAY = 5

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.cnx = None
        logging.info(f"connect db {self.host}:{self.port} {self.user} ")
        self.connect_and_initialize()

    def retry_on_failure(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    if self.cnx is None or not self.cnx.open:
                        self.connect()
                    result = func(self, *args, **kwargs)
                    logging.info(f"{func.__name__} executed successfully")
                    return result
                except (pymysql.MySQLError, pymysql.OperationalError) as error:
                    logging.error(f"Error occurred in {func.__name__}: {str(error)}")
                    if retries < self.MAX_RETRIES - 1:
                        logging.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                        time.sleep(self.RETRY_DELAY)
                        retries += 1
                    else:
                        raise Exception(f"Could not execute {func.__name__} after {self.MAX_RETRIES} attempts")

        return wrapper

    def connect(self):
        self.cnx = pymysql.connect(
            host=self.host,
            port=int(self.port),
            user=self.user,
            password=self.password,
            db=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @retry_on_failure
    def connect_and_initialize(self):
        self.connect()

        create_table_queries = [
            """
                CREATE TABLE IF NOT EXISTS guardians(
                  address VARCHAR(255) PRIMARY KEY,
                  info VARCHAR(255) NOT NULL,
                  type VARCHAR(50) NOT NULL,
                  signature VARCHAR(255) NOT NULL
                );
            """,
            """
                CREATE TABLE IF NOT EXISTS guardian_wallet(
                  guardian_address VARCHAR(255) NOT NULL,
                  wallet_address VARCHAR(255) NOT NULL,
                  chain VARCHAR(16) NOT NULL,
                  PRIMARY KEY (guardian_address, wallet_address, chain)
                );
            """,
            """
                CREATE TABLE IF NOT EXISTS wallets(
                  address VARCHAR(255) NOT NULL,
                  chain VARCHAR(16) NOT NULL,
                  threshold INT NOT NULL,
                  PRIMARY KEY (address, chain)
                );
            """
        ]
        with self.cnx.cursor() as cursor:
            for query in create_table_queries:
                cursor.execute(query)

        self.cnx.commit()

        logging.info("table get or create successfully")

    @retry_on_failure
    def execute_query(self, query, params=None):
        with self.cnx.cursor() as cursor:
            cursor.execute(query, params)
        self.cnx.commit()

    def add_guardian(self, address, guardian_type, guardian_info, signature):
        insert_query = "INSERT IGNORE INTO guardians (address, type, info, signature) VALUES (%s, %s, %s, %s)"
        insert_data = (address, guardian_type, guardian_info, signature)
        self.execute_query(insert_query, insert_data)

    @retry_on_failure
    def add_wallet_guardian(self, guardian_address, wallet_address, chain):
        insert_query = "INSERT IGNORE INTO guardian_wallet (guardian_address, wallet_address, chain) VALUES (%s, %s, %s)"
        self.execute_query(insert_query, (guardian_address, wallet_address, chain))

    @retry_on_failure
    def change_threshold(self, address, threshold, chain):
        query = "INSERT INTO wallets (address, threshold, chain) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE threshold = %s"
        self.execute_query(query, (address, threshold, chain, threshold))

    @retry_on_failure
    def del_wallet_guardian(self, guardian_address, wallet_address, chain):
        delete_query = "DELETE FROM guardian_wallet WHERE guardian_address = %s AND wallet_address = %s AND chain = %s"
        self.execute_query(delete_query, (guardian_address, wallet_address, chain))

    @retry_on_failure
    def get_guardians_by_wallet(self, wallet_address, chain):
        guardian_query = """
            SELECT guardians.address, guardians.type, guardians.info 
            FROM guardian_wallet JOIN guardians 
            ON guardian_wallet.guardian_address = guardians.address 
            AND guardian_wallet.chain = guardians.chain
            WHERE guardian_wallet.wallet_address = %s AND guardian_wallet.chain = %s
        """
        threshold_query = """
            SELECT threshold 
            FROM wallets WHERE wallets.address = %s AND wallets.chain = %s
        """

        with self.cnx.cursor() as cursor:
            cursor.execute(guardian_query, (wallet_address, chain,))
            guardians = cursor.fetchall()
            cursor.execute(threshold_query, (wallet_address, chain, ))
            threshold = cursor.fetchall()[0]['threshold']

        return threshold, guardians

    @retry_on_failure
    def get_wallets_by_guardian(self, guardian_address, chain):
        query = "SELECT wallet_address FROM guardian_wallet WHERE guardian_address = %s AND chain = %s"
        with self.cnx.cursor() as cursor:
            cursor.execute(query, (guardian_address, chain))
            results = cursor.fetchall()

        return [row['wallet_address'] for row in results]

    @retry_on_failure
    def get_guardians_by_address(self, address):
        query = "SELECT * FROM guardians WHERE address = %s"
        with self.cnx.cursor() as cursor:
            cursor.execute(query, (address,))
            results = cursor.fetchall()

        return results

