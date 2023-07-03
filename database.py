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
