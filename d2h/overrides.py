import frappe

def on_submit_purchase_receipt(doc, method):
    for item in doc.items:
        if item.purchase_order:
            item_order = frappe.get_doc("Purchase Order Item", {
                "item_code": item.item_code,
                "parent": item.purchase_order
            })
            if(item_order.custom_good_in_transit_qty > item.qty):
                item_order.custom_good_in_transit_qty -= item.qty
            else:
                item_order.custom_good_in_transit_qty = 0
            item_order.save()

def validate_purchase_receipt(doc, method):
    user_roles = frappe.get_roles(frappe.session.user)
    if "Store Dept" in user_roles and "Administrator" not in user_roles:
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

def on_delete_purchase_receipt(doc, method):
    on_submit_purchase_receipt(doc, method)

def sales_order_before_load(user):
    if "Store Dept" in frappe.get_roles(user) and frappe.session.user != "Administrator":
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
        ""
