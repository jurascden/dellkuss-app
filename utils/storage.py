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
def get_all_invoices(limit: int = 50):
    res = (
        supabase
        .table("invoices")
        .select("id, invoice_number, invoice_date, customer_name, total")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    data = res.data or []
    return [
        (
            d["id"],
            d["invoice_number"],
            d["invoice_date"],
            d["customer_name"],
            d["total"],
        )
        for d in data
    ]


# =========================
# READ
# =========================
def get_invoice_by_number(invoice_number: str):
    res = (
        supabase
        .table("invoices")
        .select("id, invoice_number, invoice_date, customer_name, total, payload")
        .eq("invoice_number", invoice_number)
        .single()
        .execute()
    )
    return res.data


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
