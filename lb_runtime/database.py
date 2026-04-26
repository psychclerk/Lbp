import sqlite3
import logging

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lb_database")

class PSQLite:
    """Production-grade SQLite wrapper for Liberty BASIC 4 Transpiler."""
    def __init__(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path)
            # Use Row factory for better data access
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to SQLite database: {db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise

    def execute(self, sql, params=()):
        """Execute a command and return results."""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"SQL Error in execute: {e}\nSQL: {sql}")
            return []

    def command(self, sql):
        """Liberty BASIC style command routing."""
        self.execute(sql)

    def query(self, sql, params=()):
        """Perform a query without commit."""
        try:
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"SQL Error in query: {e}\nSQL: {sql}")
            return []

    def close(self):
        """Safely close the connection."""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed.")

# MySQL Implementation
try:
    import mysql.connector
    class PMySQL:
        """Production-grade MySQL wrapper for Liberty BASIC 4 Transpiler."""
        def __init__(self, host, user, password, database):
            try:
                self.conn = mysql.connector.connect(
                    host=host, user=user, password=password, database=database
                )
                self.cursor = self.conn.cursor(dictionary=True)
                logger.info(f"Connected to MySQL database: {database} on {host}")
            except mysql.connector.Error as e:
                logger.error(f"Failed to connect to MySQL: {e}")
                raise

        def execute(self, sql, params=()):
            try:
                self.cursor.execute(sql, params)
                self.conn.commit()
                return self.cursor.fetchall()
            except mysql.connector.Error as e:
                logger.error(f"MySQL Error in execute: {e}\nSQL: {sql}")
                return []

        def command(self, sql):
            self.execute(sql)

        def query(self, sql, params=()):
            try:
                self.cursor.execute(sql, params)
                return self.cursor.fetchall()
            except mysql.connector.Error as e:
                logger.error(f"MySQL Error in query: {e}\nSQL: {sql}")
                return []

        def close(self):
            if self.conn:
                self.conn.close()
                logger.info("MySQL connection closed.")
except ImportError:
    class PMySQL:
        def __init__(self, *args, **kwargs):
            logger.error("mysql-connector-python not installed. Cannot use PMySQL.")
            raise ImportError("mysql-connector-python not installed")
