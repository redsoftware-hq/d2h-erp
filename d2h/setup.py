"""D2H-6 setup helpers for the Store Member role.

Granting a role access to a *standard* ERPNext report is fragile: standard
reports are re-synced from their app JSON on upgrades, which silently drops any
role added only in the database. To keep Store Member's stock-report access
durable, `ensure_store_member_report_access` is wired to the `after_migrate`
hook so it re-asserts on every migrate. It inserts the Has Role row directly
(no Report doc.save) to avoid exporting standard report files in developer mode.
"""

import frappe

ROLE = "Store Member"

# warehouse-scoped stock reports the Store Member role should reach
STOCK_REPORTS = ["Stock Ledger", "Stock Balance"]


def ensure_store_member_report_access():
    if not frappe.db.exists("Role", ROLE):
        return
    for report in STOCK_REPORTS:
        if not frappe.db.exists("Report", report):
            continue
        already = frappe.db.exists(
            "Has Role",
            {"parent": report, "parenttype": "Report", "role": ROLE},
        )
        if not already:
            frappe.get_doc(
                {
                    "doctype": "Has Role",
                    "parent": report,
                    "parenttype": "Report",
                    "parentfield": "roles",
                    "role": ROLE,
                }
            ).insert(ignore_permissions=True)
