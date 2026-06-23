import json
from d2h.api import create_purchase_receipt
import frappe

def on_submit_purchase_receipt(doc, method):
    for item in doc.items:
        if item.purchase_order:
            item_order = frappe.get_doc("Purchase Order Item", {
                "item_code": item.item_code,
                "parent": item.purchase_order
            })
            if(item_order.custom_good_in_transit_qty > item.original_quantity):
                item_order.custom_good_in_transit_qty -= item.original_quantity
            else:
                item_order.custom_good_in_transit_qty = 0
            item_order.save(ignore_permissions=True)
    new_purchase_receipt_required = False
    new_items = []
    purchase_order = None
    for item in doc.items:
        if item.original_quantity - item.qty > 0:
            new_purchase_receipt_required = True
            purchase_order = item.purchase_order
            item_order = frappe.get_doc("Purchase Order Item", {
                "item_code": item.item_code,
                "parent": item.purchase_order
            })
            new_items.append({
                "item_code": item.item_code,
                "qty": item.original_quantity - item.qty,
                "uom": item.uom,
                "item_name": item.item_name,
                "name": item_order.name,
            })
    if new_purchase_receipt_required:
        create_purchase_receipt(purchase_order, json.dumps(new_items))

def after_insert_purchase_receipt(doc, method):
    for item in doc.items:
        item.original_quantity = item.qty
    doc.custom_item_duplicate = []
    for item in doc.items:
        new_item = doc.append("custom_item_duplicate", {})
        new_item.item_code = item.item_code
        new_item.qty = item.qty
        new_item.uom = item.uom
        new_item.base_rate = item.base_rate
        new_item.stock_uom = item.stock_uom
        new_item.conversion_factor = item.conversion_factor
        new_item.received_qty = item.received_qty
        new_item.serial_no = item.serial_no
        new_item.rejected_qty = item.rejected_qty
        new_item.purchase_order = item.purchase_order
        new_item.serial_and_batch_bundle = item.serial_and_batch_bundle
        new_item.rejected_serial_and_batch_bundle = item.rejected_serial_and_batch_bundle
        new_item.use_serial_batch_fields = item.use_serial_batch_fields
        new_item.original_quantity = item.original_quantity

    doc.save(ignore_permissions=True)

def validate_purchase_receipt(doc, method):
    user_roles = frappe.get_roles(frappe.session.user)
    if "Store Dept" in user_roles and "System Manager" not in user_roles:
        for ind in range(len(doc.custom_item_duplicate)):
            duplicate_item = doc.custom_item_duplicate[ind]
            item = doc.items[ind]
            if duplicate_item.item_code == item.item_code:
                item.qty = duplicate_item.qty
                item.serial_and_batch_bundle = duplicate_item.serial_and_batch_bundle
                item.rejected_serial_and_batch_bundle = duplicate_item.rejected_serial_and_batch_bundle
                item.use_serial_batch_fields = duplicate_item.use_serial_batch_fields
    else:
        doc.custom_item_duplicate = []
        for item in doc.items:
            new_item = doc.append("custom_item_duplicate", {})
            new_item.item_code = item.item_code
            new_item.qty = item.qty
            new_item.uom = item.uom
            new_item.base_rate = item.base_rate
            new_item.stock_uom = item.stock_uom
            new_item.conversion_factor = item.conversion_factor
            new_item.received_qty = item.received_qty
            new_item.serial_no = item.serial_no
            new_item.rejected_qty = item.rejected_qty
            new_item.purchase_order = item.purchase_order
            new_item.serial_and_batch_bundle = item.serial_and_batch_bundle
            new_item.rejected_serial_and_batch_bundle = item.rejected_serial_and_batch_bundle
            new_item.use_serial_batch_fields = item.use_serial_batch_fields
            new_item.original_quantity = item.original_quantity

def validate_delivery_note(doc, method):
    user_roles = frappe.get_roles(frappe.session.user)
    if "Store Dept" in user_roles and "System Manager" not in user_roles:
        for ind in range(len(doc.custom_delivery_note_item_duplicate)):
            duplicate_item = doc.custom_delivery_note_item_duplicate[ind]
            item = doc.items[ind]
            if duplicate_item.item_code == item.item_code:
                item.qty = duplicate_item.qty
                item.serial_and_batch_bundle = duplicate_item.serial_and_batch_bundle
                item.use_serial_batch_fields = duplicate_item.use_serial_batch_fields
    else:
        doc.custom_delivery_note_item_duplicate = []
        for item in doc.items:
            new_item = doc.append("custom_delivery_note_item_duplicate", {})
            new_item.item_code = item.item_code
            new_item.qty = item.qty
            new_item.uom = item.uom
            new_item.stock_uom = item.stock_uom
            new_item.conversion_factor = item.conversion_factor
            new_item.stock_qty = item.stock_qty
            new_item.serial_no = item.serial_no
            new_item.serial_and_batch_bundle = item.serial_and_batch_bundle
            new_item.use_serial_batch_fields = item.use_serial_batch_fields

def on_delete_purchase_receipt(doc, method):
    on_submit_purchase_receipt(doc, method)

def sales_order_before_load(user):
    user_roles = frappe.get_roles(user)
    is_admin = "System Manager" in user_roles or user == "Administrator"
    if "Store Dept" in user_roles and not is_admin:
        return """
            `tabSales Order`.name IN (
                SELECT DISTINCT sii.sales_order
                FROM `tabSales Invoice Item` sii
                JOIN `tabSales Invoice` si ON si.name = sii.parent
                WHERE si.status = 'Paid'
            )
            OR `tabSales Order`.custom_balance_status = 'Approved'
        """
    else:
        return ""
