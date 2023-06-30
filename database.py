import mysql.connector
import os
import hashlib
import logging

class Database:
    def __init__(self):

        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

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

        try:
            self.cursor.execute(create_table_query)
        except mysql.connector.Error as error:
            logging.error("create table error")

    def __del__(self):
        self.cursor.close()
        self.cnx.close()

    def add_guardian(self, address, guardian_type, guardian_info, signature):
        signature_hash = hashlib.sha256(signature.encode()).hexdigest()

        insert_query = "INSERT INTO guardians (signature_hash, address, type, info, signature) VALUES (%s, %s, %s, %s, %s)"
        insert_data = (signature_hash, address, guardian_type, guardian_info, signature)
        self.cursor.execute(insert_query, insert_data)
        self.cnx.commit()

    def get_guardians_by_address(self, address):
        query = "SELECT * FROM guardians WHERE address = %s"
        self.cursor.execute(query, (address,))
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

