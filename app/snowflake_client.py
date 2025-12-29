import os
from dotenv import load_dotenv
load_dotenv()

try:
    import snowflake.connector
except Exception:
    snowflake = None


class SnowflakeClient:
    """Simple Snowflake client helper to insert classification results.

    Configure using environment variables (or a .env file):
    - SNOWFLAKE_ACCOUNT
    - SNOWFLAKE_USER
    - SNOWFLAKE_PASSWORD
    - SNOWFLAKE_WAREHOUSE
    - SNOWFLAKE_DATABASE
    - SNOWFLAKE_SCHEMA
    - SNOWFLAKE_ROLE (optional)

    This helper will create a table if it doesn't exist and insert rows.
    """

    def __init__(self):
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")
        self.role = os.getenv("SNOWFLAKE_ROLE")

    def _conn(self):
        if snowflake is None:
            raise RuntimeError("snowflake-connector-python not installed or failed to import")
        if not all([self.account, self.user, self.password, self.warehouse, self.database, self.schema]):
            raise RuntimeError("Missing one or more Snowflake environment variables. See README.")

        conn = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
            role=self.role if self.role else None,
        )
        return conn

    def ensure_table(self, table_name="INSPECTION_FINDINGS"):
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            property_id NUMBER,
            property_name STRING,
            room_id NUMBER,
            room_name STRING,
            image_filename STRING,
            label STRING,
            score FLOAT,
            notes STRING,
            evaluated_at TIMESTAMP_LTZ DEFAULT current_timestamp()
        );
        """
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(create_sql)
            cur.close()

    def insert_findings(self, rows, table_name="INSPECTION_FINDINGS"):
        """Rows: iterable of tuples matching columns: property_id,property_name,room_id,room_name,image_filename,label,score,notes"""
        insert_sql = f"INSERT INTO {table_name} (property_id,property_name,room_id,room_name,image_filename,label,score,notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.executemany(insert_sql, rows)
            conn.commit()
            return True
        finally:
            cur.close()
            conn.close()
