"""Make the Sales Order delivery warehouse a mandatory "Delivery Location".

Client requirement (Session 2): add a mandatory "Delivery Location" field on the
Sales Order to enable delivery from a specific warehouse and link the order to the
correct stock for fulfilment. "Delivery Location" = warehouse (confirmed).

Rather than add a redundant custom field, this reuses the standard header field
`set_warehouse` (Link -> Warehouse): it is relabelled "Delivery Location" and made
mandatory. Reusing it keeps ERPNext's native behaviour of cascading the chosen
warehouse to every item row. Per-item "Delivery Warehouse" (Sales Order Item.
warehouse) stays as the native item-wise option.

Shipped as property setters via a patch (same approach as D2H-2/3/4) so the change
survives migrate and isn't overwritten. Idempotent: safe to re-run.
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DOCTYPE = "Sales Order"
FIELD = "set_warehouse"


def execute():
    if not frappe.get_meta(DOCTYPE).get_field(FIELD):
        return
    make_property_setter(
        DOCTYPE, FIELD, "label", "Delivery Location", "Data",
        validate_fields_for_doctype=False,
    )
    make_property_setter(
        DOCTYPE, FIELD, "reqd", 1, "Check",
        validate_fields_for_doctype=False,
    )
    frappe.clear_cache(doctype=DOCTYPE)
