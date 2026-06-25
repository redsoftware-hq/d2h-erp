"""D2H-3: Hide Sales Order financial fields from the Store Dept role.

Mirrors D2H-2 (Purchase Order) on the selling side: moves all monetary fields on
Sales Order / Sales Order Item to permlevel 1, then grants permlevel-1 access to
every role that already has permlevel-0 access EXCEPT "Store Dept", mirroring each
role's read/write. Only Store Dept loses visibility of amounts; quantities and
operational fields stay at permlevel 0 and remain visible to everyone.

Idempotent: safe to re-run. Roles are derived from each site's current
permissions, so it adapts across environments without hardcoding the role list.
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.permissions import add_permission, update_permission_property

RESTRICTED_ROLE = "Store Dept"

PARENT_DOCTYPE = "Sales Order"
PARENT_FIELDS = [
    "currency", "conversion_rate", "selling_price_list", "price_list_currency",
    "plc_conversion_rate", "total", "base_total", "net_total", "base_net_total",
    "taxes_and_charges", "taxes", "total_taxes_and_charges",
    "base_total_taxes_and_charges", "tax_category", "shipping_rule",
    "grand_total", "base_grand_total", "rounding_adjustment",
    "base_rounding_adjustment", "rounded_total", "base_rounded_total",
    "in_words", "base_in_words", "disable_rounded_total", "apply_discount_on",
    "additional_discount_percentage", "discount_amount", "base_discount_amount",
    "advance_paid", "amount_eligible_for_commission", "commission_rate",
    "total_commission",
]

ITEM_DOCTYPE = "Sales Order Item"
ITEM_FIELDS = [
    "rate", "amount", "base_rate", "base_amount", "price_list_rate",
    "base_price_list_rate", "net_rate", "net_amount", "base_net_rate",
    "base_net_amount", "discount_percentage", "discount_amount",
    "margin_type", "rate_with_margin",
]


def _set_permlevel(doctype, fields):
    meta = frappe.get_meta(doctype)
    for fieldname in fields:
        if meta.get_field(fieldname):
            make_property_setter(
                doctype, fieldname, "permlevel", 1, "Int",
                validate_fields_for_doctype=False,
            )


def _mirror_permlevel0_grants(doctype):
    """Grant permlevel-1 read/write to every role that has permlevel-0 read,
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
        add_permission(doctype, row.role, 1)
        update_permission_property(doctype, row.role, 1, "read", 1, validate=False)
        update_permission_property(doctype, row.role, 1, "write", row.write or 0, validate=False)


def execute():
    _set_permlevel(PARENT_DOCTYPE, PARENT_FIELDS)
    _set_permlevel(ITEM_DOCTYPE, ITEM_FIELDS)
    _mirror_permlevel0_grants(PARENT_DOCTYPE)
    frappe.clear_cache(doctype=PARENT_DOCTYPE)
