"""D2H-4: Hide Stock Entry valuation from the Store Dept role.

Hides the valuation section (Total Outgoing/Incoming Value, Value Difference and
related amounts) from Store Dept users while keeping quantities and warehouses
visible, so they can still create and submit Material Transfers.

Implementation note - why permlevel 2 (not 1 like D2H-2/D2H-3):
`Stock Entry Detail.basic_rate` already ships at permlevel 1 in standard ERPNext
and is currently hidden from every non-Administrator role (no role is granted
permlevel-1 read on this site). If we reused permlevel 1 and granted it to the
non-store roles, we would inadvertently reveal `basic_rate` to them and change
their existing behaviour. Putting the D2H valuation fields on permlevel 2 leaves
`basic_rate` exactly as-is: non-store roles keep what they see today, Store Dept
loses the valuation section, and `basic_rate` visibility is unchanged for all.

Valuation amounts are computed server-side by the Stock Entry controller, so
removing field-level access does not stop Store Dept creating/submitting entries
(they already submit entries today with basic_rate above their permlevel).

Idempotent: safe to re-run. Roles are derived from each site's current
permissions, so it adapts across environments without hardcoding the role list.
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.permissions import add_permission, update_permission_property

RESTRICTED_ROLE = "Store Dept"
TARGET_PERMLEVEL = 2

PARENT_DOCTYPE = "Stock Entry"
PARENT_FIELDS = [
    "total_outgoing_value", "total_incoming_value", "value_difference",
    "total_amount", "total_additional_costs",
]

ITEM_DOCTYPE = "Stock Entry Detail"
# NOTE: basic_rate is deliberately excluded - it is already permlevel 1.
ITEM_FIELDS = [
    "basic_amount", "valuation_rate", "amount", "additional_cost",
]


def _set_permlevel(doctype, fields):
    meta = frappe.get_meta(doctype)
    for fieldname in fields:
        if meta.get_field(fieldname):
            make_property_setter(
                doctype, fieldname, "permlevel", TARGET_PERMLEVEL, "Int",
                validate_fields_for_doctype=False,
            )


def _mirror_permlevel0_grants(doctype):
    """Grant TARGET_PERMLEVEL read/write to every role that has permlevel-0 read,
    except the restricted role, mirroring its existing read/write."""
    source = "Custom DocPerm" if frappe.get_all(
        "Custom DocPerm", filters={"parent": doctype}, limit=1
    ) else "DocPerm"

    rows = frappe.get_all(
        source,
        filters={"parent": doctype, "permlevel": 0, "read": 1},
        fields=["role", "write"],
    )
    for row in rows:
        if row.role == RESTRICTED_ROLE:
            continue
        add_permission(doctype, row.role, TARGET_PERMLEVEL)
        update_permission_property(doctype, row.role, TARGET_PERMLEVEL, "read", 1, validate=False)
        update_permission_property(doctype, row.role, TARGET_PERMLEVEL, "write", row.write or 0, validate=False)


def execute():
    _set_permlevel(PARENT_DOCTYPE, PARENT_FIELDS)
    _set_permlevel(ITEM_DOCTYPE, ITEM_FIELDS)
    _mirror_permlevel0_grants(PARENT_DOCTYPE)
    frappe.clear_cache(doctype=PARENT_DOCTYPE)
