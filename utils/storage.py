from supabase import create_client
import streamlit as st
from datetime import datetime
from postgrest.exceptions import APIError

# Supabase Client
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_SECRET_KEY"]
)

TABLE = "invoices"


# =========================
# CREATE / SAVE
# =========================
def save_invoice(
    invoice_number: str,
    invoice_date: str,
    customer_name: str,
    total: float,
    payload: dict,
    mode: str = "create"   # "create" | "update"
):
    try:
        if mode == "create":
            supabase.table(TABLE).insert({
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "customer_name": customer_name,
                "total": total,
                "payload": payload
            }).execute()

        elif mode == "update":
            res = supabase.table(TABLE) \
                .update({
                    "invoice_date": invoice_date,
                    "customer_name": customer_name,
                    "total": total,
                    "payload": payload
                }) \
                .eq("invoice_number", invoice_number) \
                .execute()

            # WICHTIG: prüfen, ob wirklich aktualisiert wurde
            if not res.data:
                return "NOT_FOUND"

        return True

    except APIError as e:
        if "duplicate key value" in str(e):
            return "DUPLICATE_INVOICE_NUMBER"
        raise


# =========================
# READ ALL
# =========================
def get_all_invoices():
    res = (
        supabase
        .table(TABLE)
        .select("id, invoice_number, invoice_date, customer_name, total, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    if not res.data:
        return []

    return [
        (
            row["id"],
            row["invoice_number"],
            row["invoice_date"],
            row["customer_name"],
            row["total"],
            row["created_at"],
        )
        for row in res.data
    ]


# =========================
# READ
# =========================
def get_invoice_by_number(invoice_number: str):
    if not invoice_number:
        return None

    result = (
        supabase
        .table(TABLE)
        .select("*")
        .eq("invoice_number", invoice_number)
        .maybe_single()
        .execute()
    )

    return result.data


# =========================
# DELETE
# =========================
def delete_invoice(invoice_number: str):
    (
        supabase
        .table(TABLE)
        .delete()
        .eq("invoice_number", invoice_number)
        .execute()
    )
