import sqlite3
from typing import Any
from app.api.schemas.shipment import ShipmentCreate
from contextlib import contextmanager

class Database:

    def connect_to_db(self):
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        print("Connected to the db...")

    def create_table(self):
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS shipment
                         (
                             id      INTEGER PRIMARY KEY AUTOINCREMENT,
                             content TEXT,
                             weight  REAL,
                             status  TEXT
                         )
                         """)
        self.conn.commit()

    def create(self, shipment: ShipmentCreate) -> int:
        # Convert Pydantic object to a dictionary safely
        shipment_data = shipment.model_dump()

        self.cur.execute("""
                         INSERT INTO shipment (content, weight, status)
                         VALUES (:content, :weight, :status)
                         """, {
                             "content": shipment_data["content"],
                             "weight": shipment_data["weight"],
                             "status": "placed",
                         })
        self.conn.commit()
        return self.cur.lastrowid  # Let SQLite assign the ID cleanly

    def get(self, shipment_id: int) -> dict[str, Any] | None:
        self.cur.execute("SELECT * FROM shipment WHERE id = ?", (shipment_id,))
        row = self.cur.fetchone()

        # Convert sqlite3.Row into a standard Python dict for FastAPI
        return row if row else None

    def update(self, shipment_id: int, body: dict[str, Any]) -> dict[str, Any] | None:
        # Update using a dynamic status payload dictionary safely
        self.cur.execute("""
                         UPDATE shipment
                         SET status = :status
                         WHERE id = :id
                         """, {
                             "id": shipment_id,
                             "status": body.get("status")
                         })
        self.conn.commit()
        return self.get(shipment_id)

    def delete(self, shipment_id: int):
        self.cur.execute("DELETE FROM shipment WHERE id = ?", (shipment_id,))
        self.conn.commit()

    def close(self):
        print("...Connection closed")
        self.conn.close()

    # def __enter__(self):
    #     print("Entered the context...")
    #     self.connect_to_db()
    #     self.create_table()
    #     return self
    #
    # def __exit__(self, *args):
    #     self.close()
    #     print("Exited the context...")

@contextmanager
def managed_db():
    db = Database()
    print("Entered the context...")
    db.connect_to_db()
    db.create_table()
    yield db
    print("Exited the context...")
    db.close()

with managed_db() as db:
    print(db.get(1))