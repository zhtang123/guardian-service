import pymysql.cursors
import os
import hashlib
import logging
import time

class Database:
    MAX_RETRIES = 5
    RETRY_DELAY = 5

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        logging.info(f"connect db {self.host}:{self.port} {self.user} ")
        self.connect_and_initialize()

    def connect_and_initialize(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.cnx = pymysql.connect(
                    host=self.host,
                    port=int(self.port),
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )

                with self.cnx.cursor() as cursor:

                    create_table_query = """
                        CREATE TABLE IF NOT EXISTS guardians(
                          address VARCHAR(255) PRIMARY KEY,
                          info VARCHAR(255) NOT NULL,
                          type VARCHAR(50) NOT NULL,
                          signature VARCHAR(255) NOT NULL
                        );
                    """

                    cursor.execute(create_table_query)

                    create_table_query = """
                        CREATE TABLE IF NOT EXISTS guardian_wallet(
                          guardian_address VARCHAR(255) NOT NULL,
                          wallet_address VARCHAR(255) NOT NULL,
                          PRIMARY KEY (guardian_address, wallet_address)
                        );
                    """

                    cursor.execute(create_table_query)

                self.cnx.commit()
                retries = 0
                break
            except pymysql.MySQLError as error:
                logging.error("Failed to connect to database: {}".format(error))
                if retries < self.MAX_RETRIES - 1:
                    logging.info("Retrying in {} seconds...".format(self.RETRY_DELAY))
                    time.sleep(self.RETRY_DELAY)
                    retries += 1
                else:
                    raise Exception("Could not connect to the database after {} attempts".format(self.MAX_RETRIES))

    def execute_query(self, query, params=None):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                with self.cnx.cursor() as cursor:
                    cursor.execute(query, params)
                self.cnx.commit()
                retries = 0
                return True
            except pymysql.MySQLError as error:
                logging.error("Failed to execute query: {}".format(error))
                if retries < self.MAX_RETRIES - 1:
                    logging.info("Retrying in {} seconds...".format(self.RETRY_DELAY))
                    time.sleep(self.RETRY_DELAY)
                    retries += 1
                else:
                    raise Exception("Could not execute the query after {} attempts".format(self.MAX_RETRIES))
        return False

    def __del__(self):
        self.cnx.close()

    def add_guardian(self, address, guardian_type, guardian_info, signature):

        insert_query = "INSERT IGNORE INTO guardians (address, type, info, signature) VALUES (%s, %s, %s, %s)"
        insert_data = (address, guardian_type, guardian_info, signature)

        self.execute_query(insert_query, insert_data)

    def add_wallet_guardian(self, guardian_address, wallet_address):
        insert_query = "INSERT IGNORE INTO guardian_wallet (guardian_address, wallet_address) VALUES (%s, %s)"
        insert_data = (guardian_address, wallet_address)
        self.execute_query(insert_query, insert_data)

    def del_wallet_guardian(self, guardian_address, wallet_address):
        delete_query = "DELETE FROM guardian_wallet WHERE guardian_address = %s AND wallet_address = %s"
        delete_data = (guardian_address, wallet_address)
        self.execute_query(delete_query, delete_data)

    def del_all_guardians(self, wallet_address):
        delete_query = "DELETE FROM guardian_wallet WHERE wallet_address = %s"
        delete_data = (wallet_address,)
        self.execute_query(delete_query, delete_data)


    def get_guardians_by_wallet(self, wallet_address):
        query = """
            SELECT guardians.address, guardians.type, guardians.info 
            FROM guardian_wallet JOIN guardians ON guardian_wallet.guardian_address = guardians.address 
            WHERE guardian_wallet.wallet_address = %s
        """
        results = None
        with self.cnx.cursor() as cursor:
            cursor.execute(query, (wallet_address,))
            results = cursor.fetchall()

        guardians = []
        for row in results:
            guardian = {
                'guardian': row['address'],
                'type': row['type'],
                'info': row['info']
            }
            guardians.append(guardian)
        return guardians

    def get_wallets_by_guardian(self, guardian_address):
        query = "SELECT wallet_address FROM guardian_wallet WHERE guardian_address = %s"
        results = None
        with self.cnx.cursor() as cursor:
            cursor.execute(query, (guardian_address,))
            results = cursor.fetchall()
        return [wallet_address['wallet_address'] for wallet_address in results]


    def get_guardians_by_address(self, address):
        query = "SELECT * FROM guardians WHERE address = %s"
        results = None
        with self.cnx.cursor() as cursor:
            cursor.execute(query, (address,))
            results = cursor.fetchall()

        guardians = []
        for row in results:
            guardian = {
                'guardian': address,
                'type': row['type'],
                'info': row['info']
            }
            guardians.append(guardian)

        return guardians
