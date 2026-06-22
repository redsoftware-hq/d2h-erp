"""D2H-5: Make the default "Get Items" GIT-aware.

ERPNext's standard "Get Items From -> Purchase Order / Sales Order" computes the
quantity to pull as (ordered - received/delivered). It does not know about this
app's custom `custom_good_in_transit_qty` field, so whenever goods are already in
transit it over-pulls by the in-transit amount (double-counting goods already
placed on a transit document).

These thin wrappers call the original ERPNext mapping and then subtract the
in-transit quantity from each pulled row, dropping rows that are fully covered by
in-transit stock. The GIT flow itself is untouched - only the proposed quantity
is corrected.

Wired via `override_whitelisted_methods` in hooks.py, so only the client-side
"Get Items" calls are affected; direct programmatic callers keep the original.
"""

import frappe
from frappe.utils import flt

SOURCE_DOCTYPE = {
    "purchase_order_item": "Purchase Order Item",
    "so_detail": "Sales Order Item",
}


def _reduce_items_by_git(doc, source_field):
    """Subtract custom_good_in_transit_qty from each mapped row; drop rows that
    become zero/negative. Keeps stock_qty consistent with the new qty."""
    source_dt = SOURCE_DOCTYPE[source_field]
    kept = []
    for item in doc.get("items", []):
        source_name = item.get(source_field)
        in_transit = 0.0
        if source_name:
            in_transit = flt(
                frappe.db.get_value(source_dt, source_name, "custom_good_in_transit_qty")
            )
        new_qty = flt(item.qty) - in_transit
        if new_qty > 0:
            item.qty = new_qty
            item.stock_qty = new_qty * flt(item.conversion_factor) or new_qty
            kept.append(item)

    doc.items = kept
    for idx, item in enumerate(kept, start=1):
        item.idx = idx
    return doc


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
    from erpnext.buying.doctype.purchase_order.purchase_order import (
        make_purchase_receipt as _make_purchase_receipt,
    )

    doc = _make_purchase_receipt(source_name, target_doc)
    return _reduce_items_by_git(doc, "purchase_order_item")


@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, kwargs=None):
    from erpnext.selling.doctype.sales_order.sales_order import (
        make_delivery_note as _make_delivery_note,
    )

    doc = _make_delivery_note(source_name, target_doc, kwargs)
    return _reduce_items_by_git(doc, "so_detail")
