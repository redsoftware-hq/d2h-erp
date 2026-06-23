"""D2H-6: Create the warehouse-scoped "Store Member" role.

Store Member is a NEW role (distinct from "Store Dept"). It is a single-warehouse
operator: it can run the receiving / delivery / stock-transfer workflow and view
warehouse-scoped stock reports, but has no financial visibility, no accounting,
no deletion rights, and no admin functions. Per-warehouse data isolation is
achieved separately, per user, via a User Permission on Warehouse (a runtime
setup step, not part of this role definition). Testing showed the global
"Apply Strict User Permissions" setting must stay OFF: strict mode blocks the
operator from reading their own assigned warehouse. Lenient mode still scopes
stock, ledger and warehouse data to the assigned warehouse.

Permission set (permlevel 0). Items marked (functional) are not spelled out in
the client spec but are required for the spec'd workflow to actually work.
Financial fields stay hidden automatically: D2H-2/3/4 put them on higher
permlevels and this role is granted none of those.

Idempotent: safe to re-run.
"""

import frappe
from frappe.permissions import add_permission, update_permission_property

from d2h.setup import ROLE

# doctype -> {ptype: value}
PERMS = {
    # masters (read)
    "Item": {"read": 1},
    "Item Group": {"read": 1},
    "UOM": {"read": 1},
    "Warehouse": {"read": 1},
    "Company": {"read": 1},           # functional: read/select so forms work (not setup)
    "Customer": {"read": 1},          # functional: needed to create Delivery Notes
    "Supplier": {"read": 1},          # functional: needed to create Purchase Receipts
    "Batch": {"read": 1},             # functional: batch items
    # serial / batch handling
    "Serial No": {"read": 1, "write": 1},
    "Serial and Batch Bundle": {"read": 1, "write": 1, "create": 1, "submit": 1},  # functional
    # stock data behind the reports (warehouse-scoped via User Permission)
    "Stock Ledger Entry": {"read": 1},   # functional: stock ledger reports
    "Bin": {"read": 1},                  # functional: stock levels
    # transactions
    "Purchase Order": {"read": 1},                                   # read-only per spec
    "Purchase Receipt": {"read": 1, "write": 1, "create": 1, "submit": 1},
    "Delivery Note": {"read": 1, "write": 1, "create": 1, "submit": 1},
    "Stock Entry": {"read": 1, "write": 1, "create": 1, "submit": 1},
}


def _ensure_role():
    if not frappe.db.exists("Role", ROLE):
        role = frappe.new_doc("Role")
        role.role_name = ROLE
        role.desk_access = 1
        role.insert(ignore_permissions=True)


def _set_perms():
    for doctype, ptypes in PERMS.items():
        add_permission(doctype, ROLE, 0)
        for ptype, value in ptypes.items():
            update_permission_property(doctype, ROLE, 0, ptype, value, validate=False)


def execute():
    _ensure_role()
    _set_perms()
    # Stock report access is granted via the after_migrate hook
    # (d2h.setup.ensure_store_member_report_access) so it survives re-syncs of
    # the standard reports on erpnext upgrades.
    from d2h.setup import ensure_store_member_report_access
    ensure_store_member_report_access()
    frappe.clear_cache()
