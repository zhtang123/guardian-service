import mysql.connector
import os

class Database:
    def __init__(self):

        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

        print(self.host)

        self.cnx = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

        self.cursor = self.cnx.cursor()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS guardians (
              address VARCHAR(255) NOT NULL,
              info VARCHAR(255) NOT NULL,
              type VARCHAR(50) NOT NULL,
              PRIMARY KEY (address, info)
            );
        """

        try:
            self.cursor.execute(create_table_query)
        except mysql.connector.Error as error:
            print("Error creating table:", error)

    def __del__(self):
        self.cursor.close()
        self.cnx.close()

    def add_guardian(self, address, guardian_type, guardian_info):
        insert_query = "INSERT INTO guardians (address, type, info) VALUES (%s, %s, %s)"
        insert_data = (address, guardian_type, guardian_info)
        self.cursor.execute(insert_query, insert_data)
        self.cnx.commit()

    def get_guardians_by_address(self, address):
        query = "SELECT * FROM guardians WHERE address = %s"
        self.cursor.execute(query, (address,))
        results = self.cursor.fetchall()

        guardians = []
        for row in results:
            guardian = {
                'type': row[1],
                'info': row[2]
            }
            guardians.append(guardian)

        return guardians

    def get_addresses_by_guardian(self, guardian_type):
        query = "SELECT address FROM guardians WHERE type = %s"
        self.cursor.execute(query, (guardian_type,))
        results = self.cursor.fetchall()

        addresses = [row[0] for row in results]

        return addresses
