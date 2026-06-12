import sqlite3


DB_PATH = "database/documents.db"


def init_db():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        document_type TEXT,
        date TEXT,

        amount TEXT,
        contract_value TEXT,

        sender TEXT,
        receiver TEXT,

        invoice_number TEXT,

        report_title TEXT,
        summary TEXT,

        anomalies TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_document(data, anomalies):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO documents(
        document_type,
        date,
        amount,
        contract_value,
        sender,
        receiver,
        invoice_number,
        report_title,
        summary,
        anomalies
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("document_type"),

        data.get("date"),

        data.get("amount"),

        data.get("contract_value"),

        data.get("sender"),

        data.get("receiver"),

        data.get("invoice_number"),

        data.get("report_title"),

        data.get("summary"),

        ", ".join(anomalies)
    ))

    cursor.close()
    conn.commit()
    conn.close()