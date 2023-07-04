import mysql.connector
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
        self.connect_and_initialize()

    def connect_and_initialize(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.cnx = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )

                self.cursor = self.cnx.cursor()

                create_table_query = """
                    CREATE TABLE IF NOT EXISTS guardians(
                      signature_hash VARCHAR(64) PRIMARY KEY,
                      address VARCHAR(255) NOT NULL,
                      info VARCHAR(255) NOT NULL,
                      type VARCHAR(50) NOT NULL,
                      signature VARCHAR(255) NOT NULL
                    );
                """

                self.cursor.execute(create_table_query)

                create_table_query = """
                    CREATE TABLE IF NOT EXISTS guardian_wallet(
                      guardian_address VARCHAR(255) NOT NULL,
                      wallet_address VARCHAR(255) NOT NULL,
                      PRIMARY KEY (guardian_address, wallet_address)
                    );
                """

                self.cursor.execute(create_table_query)
                retries = 0
                break
            except mysql.connector.Error as error:
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
                if self.cnx.is_connected() == False:
                    self.connect_and_initialize()
                self.cursor.execute(query, params)
                retries = 0
                return True
            except mysql.connector.Error as error:
                logging.error("Failed to execute query: {}".format(error))
                if retries < self.MAX_RETRIES - 1:
                    logging.info("Retrying in {} seconds...".format(self.RETRY_DELAY))
                    time.sleep(self.RETRY_DELAY)
                    retries += 1
                else:
                    raise Exception("Could not execute the query after {} attempts".format(self.MAX_RETRIES))
        return False

    def __del__(self):
        self.cursor.close()
        self.cnx.close()

    def add_guardian(self, address, guardian_type, guardian_info, signature):
        signature_hash = hashlib.sha256(signature.encode()).hexdigest()

        insert_query = "INSERT IGNORE INTO guardians (signature_hash, address, type, info, signature) VALUES (%s, %s, %s, %s, %s)"
        insert_data = (signature_hash, address, guardian_type, guardian_info, signature)

        self.execute_query(insert_query, insert_data)
        self.cnx.commit()

    def add_wallet_guardian(self, guardian_address, wallet_address):
        insert_query = "INSERT IGNORE INTO guardian_wallet (guardian_address, wallet_address) VALUES (%s, %s)"
        insert_data = (guardian_address, wallet_address)
        self.execute_query(insert_query, insert_data)
        self.cnx.commit()


    def get_guardians_by_wallet(self, wallet_address):
        query = """
            SELECT guardians.address, guardians.type, guardians.info 
            FROM guardian_wallet JOIN guardians ON guardian_wallet.guardian_address = guardians.address 
            WHERE guardian_wallet.wallet_address = %s
        """
        if self.execute_query(query, (wallet_address,)):
            results = self.cursor.fetchall()

            guardians = []
            for row in results:
                guardian = {
                    'guardian': row[0],
                    'type': row[1],
                    'info': row[2]
                }
                guardians.append(guardian)
            return guardians

    def get_wallets_by_guardian(self, guardian_address):
        query = "SELECT wallet_address FROM guardian_wallet WHERE guardian_address = %s"
        if self.execute_query(query, (guardian_address,)):
            results = self.cursor.fetchall()
            return [wallet_address[0] for wallet_address in results]


    def get_guardians_by_address(self, address):
        query = "SELECT * FROM guardians WHERE address = %s"

        if self.execute_query(query, (address,)):
            results = self.cursor.fetchall()

            guardians = []
            for row in results:
                guardian = {
                    'guardian': address,
                    'type': row[1],
                    'info': row[2]
                }
                guardians.append(guardian)

            return guardians
