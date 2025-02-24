from erpnext.accounts.party import get_dashboard_info
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today
import json

from frappe.utils.data import flt

LIMIT_PER_DAY = 2

@frappe.whitelist()
def increment_print_count():
    current_date = today()

    print_log = frappe.cache().hget('global_daily_print_log', 'count') or {}

    if print_log.get('date') != current_date:
        print_log = {'count': 0, 'date': current_date}

    if print_log['count'] > LIMIT_PER_DAY:
        return {'limit_reached': True}

    print_log['count'] += 1
    frappe.cache().hset('global_daily_print_log', 'count', print_log)

    return {'limit_reached': False}

def before_print(_, __, ___):
    current_date = today()

    print_log = frappe.cache().hget('global_daily_print_log', 'count')

    if not print_log:
        return

    if print_log.get('date') != current_date:
        return

    if print_log['count'] > LIMIT_PER_DAY:
        frappe.throw('The daily print limit for all documents has been reached.')

@frappe.whitelist()
def get_print_limit():
    current_date = today()

    print_log = frappe.cache().hget('global_daily_print_log', 'count')

    if not print_log:
        return { "limit_reached" : False }

    if print_log.get('date') != current_date:
        return { "limit_reached" : False }

    if print_log['count'] > LIMIT_PER_DAY:
        return { "limit_reached" : True }


@frappe.whitelist()
def short_close_purchase_order(purchase_order):
    purchase_order = frappe.get_doc("Purchase Order", purchase_order)
    for item in purchase_order.items:
        if item.qty > item.received_qty:
            item.custom_short_close_qty = item.qty - item.received_qty - item.custom_good_in_transit_qty

    purchase_order.save(ignore_permissions=True)
    return "OK"

def set_missing_values(source, target):
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")


@frappe.whitelist()
def create_purchase_receipt(purchase_order, items):
    purchase_order = frappe.get_doc("Purchase Order", purchase_order)
    items_list = json.loads(items)
    def update_item(obj, target, source_parent):
        givern_item = next((i for i in items_list if i.get("name") == obj.name), None)
        new_qty = givern_item.get("qty") if givern_item else flt(obj.received_qty)
        target.qty = flt(new_qty)
        target.stock_qty = (flt(obj.qty) - flt(new_qty)) * flt(obj.conversion_factor)
        target.amount = (flt(obj.qty) - flt(new_qty)) * flt(obj.rate)
        target.base_amount = (
            (flt(obj.qty) - flt(new_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
        )
    doc = get_mapped_doc(
        "Purchase Order",
        purchase_order.name,
        {
            "Purchase Order": {
                "doctype": "Purchase Receipt",
                "field_map": {"supplier_warehouse": "supplier_warehouse"},
                "validation": {
                    "docstatus": ["=", 1],
                },
            },
            "Purchase Order Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
                    "bom": "bom",
                    "material_request": "material_request",
                    "material_request_item": "material_request_item",
                    "sales_order": "sales_order",
                    "sales_order_item": "sales_order_item",
                    "wip_composite_asset": "wip_composite_asset",
                },
                "postprocess": update_item,
                "condition": lambda doc: abs(doc.received_qty) < abs(doc.qty) and next((i for i in items_list if i["name"] == doc.name), False)
                and doc.delivered_by_supplier != 1,
            },
            "Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
        },
        None,
        set_missing_values,
    )
    doc.save(ignore_permissions=True)
    
    for item in purchase_order.items:
        found_item = next((itm for itm in items_list if itm['name'] == item.name), None)
        if found_item:
            item.custom_good_in_transit_qty += found_item['qty']

    purchase_order.save(ignore_permissions=True)
    return "OK"

@frappe.whitelist()
def get_purchase_order_good_in_transit(purchase_order):
    purchase_receipts = frappe.get_all(
        "Purchase Receipt Item",
        filters={
            "purchase_order": purchase_order,
            "docstatus": 1
        },
        fields=["name", "item_code", "item_name", "qty", "purchase_order_item"]
    )
    return purchase_receipts


@frappe.whitelist()
def short_close_sales_order(sales_order):
    sales_order = frappe.get_doc("Sales Order", sales_order)
    for item in sales_order.items:
        if item.qty > item.delivered_qty:
            item.custom_short_close_qty = item.qty - item.delivered_qty

    sales_order.save(ignore_permissions=True)
    return "OK"

@frappe.whitelist()
def get_sales_order_good_in_transit(sales_order):
    delivery_notes = frappe.get_all(
        "Delivery Note Item",
        filters={
            "against_sales_order": sales_order,
            "docstatus": 1
        },
        fields=["name", "item_code", "item_name", "qty", "so_detail"]
    )
    return delivery_notes

@frappe.whitelist()
def customer_has_balance(customer, sales_order):
    info = get_dashboard_info("Customer", customer)
    order = frappe.get_doc("Sales Order", sales_order)
    invoice_exists = frappe.db.exists("Sales Invoice Item", {"sales_order": sales_order, "docstatus": 1})
    pending_amount = order.total
    total = order.total
    if invoice_exists:
        invoice_item = frappe.get_doc("Sales Invoice Item", {"sales_order": sales_order, "docstatus": 1})
        invoice = frappe.get_doc("Sales Invoice", { "name": invoice_item.parent })
        pending_amount = invoice.outstanding_amount
        total = invoice.total
    return { "balance": info[0]["total_unpaid"], "pending": pending_amount, "total": total }