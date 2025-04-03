frappe.ui.form.on("Sales Order", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1 && frm.doc.status != "Closed") {
      frappe.call({
        method: "d2h.api.get_sales_order_good_in_transit",
        args: {
          sales_order: frm.doc.name,
        },
        callback: function (r) {
          pending_qty = [];
          frm.doc.items.map((item) => {
            received_qty = 0;
            r.message.map((i) => {
              if (i.so_detail == item.name) {
                received_qty += i.qty;
              }
            });
            if (received_qty < item.qty) {
              pending_qty.push({
                name: item.name,
                pending: item.qty - received_qty,
              });
            }
          });
          if (pending_qty.length > 0) {
            frm.add_custom_button(__("Short Close"), function () {
              show_confirm_dialog(frm);
            });
          }
        },
      });
      frappe.call({
        method: "d2h.api.customer_has_balance",
        args: {
          customer: frm.doc.customer,
          sales_order: frm.doc.name,
        },
        callback: function (r) {
          if (r.message && r.message.balance < 0) {
            if (frappe.user_roles.includes("Finance Dept")) {
              frm.add_custom_button(__("Allow Delivery"), function () {
                if (frm.doc.custom_balance_status == "Applied") {
                  frappe.msgprint(
                    __("Delivery Request is already has been sent.")
                  );
                } else if (frm.doc.custom_balance_status == "Approved") {
                  frappe.msgprint(
                    __("Delivery Request is already has been approved.")
                  );
                } else {
                  show_allow_delivery_confirm_dialog(frm, r.message);
                }
              });
              if (
                frm.doc.custom_balance_status == "Applied" ||
                frm.doc.custom_balance_status == "Approved"
              ) {
                $(`button[data-label='Allow%20Delivery']`).css({
                  "background-color": "#b9ecca",
                  color: "#16794c",
                });
              }
            }
            if (frappe.user_roles.includes("Finance Manager")) {
              frm.add_custom_button(__("Approve Delivery"), function () {
                if (frm.doc.custom_balance_status == "Approved") {
                  frappe.msgprint(
                    __("Delivery Request is already has been approved.")
                  );
                } else {
                  show_approve_delivery_confirm_dialog(frm, r.message);
                }
              });
              if (frm.doc.custom_balance_status == "Approved") {
                $(`button[data-label='Approve%20Delivery']`).css({
                  "background-color": "#b9ecca",
                  color: "#16794c",
                });
              }
            }
          }
        },
      });
    }
    setTimeout(() => {
      $(`[data-label='Status'].inner-group-button`).hide();
      $(`[data-label='Status%20%3E%20Re-open'].menu-item-label`)
        .parent()
        .hide();
      $(`[data-label='Status%20%3E%20Close'].menu-item-label`).parent().hide();
      $(`[data-label='Status%20%3E%20Hold'].menu-item-label`).parent().hide();
    }, 200);
  },
  onload: function (frm) {
    setTimeout(() => {
      $(`[data-label='Status'].inner-group-button`).hide();
      $(`[data-label='Status%20%3E%20Re-open'].menu-item-label`)
        .parent()
        .hide();
      $(`[data-label='Status%20%3E%20Close'].menu-item-label`).parent().hide();
      $(`[data-label='Status%20%3E%20Hold'].menu-item-label`).parent().hide();
    }, 200);
  },
  set_warehouse: function (frm) {
    if (frm.doc.set_warehouse) {
      if (frm.doc.items.length > 0) {
        frm.doc.items.map((item) => {
          update_warehouse_balance(frm, item);
        });
      }
    }
  },
});

function show_confirm_dialog(frm) {
  frappe.confirm(
    "Are you sure? This will short close all pending items.",
    function () {
      frappe.call({
        method: "d2h.api.short_close_sales_order",
        args: {
          sales_order: frm.doc.name,
        },
        callback: function (r) {
          frappe.msgprint(
            __(`Sales Order ${frm.doc.name} has been short closed.`)
          );
          cur_frm.cscript.update_status("Close", "Closed");

          frm.refresh();
          d.hide();
        },
      });
    }
  );
}

function show_allow_delivery_confirm_dialog(frm, data) {
  frappe.confirm(
    `Are you sure? This will send a request to allow the delivery. <br/>Customer Balance: ${Math.abs(
      data.balance
    )} <br/>Sales Order Amount: ${Math.abs(
      data.total
    )} <br/>Sales Order Paid: ${Math.abs(
      data.total - data.pending
    )} <br/>Amount Pending: ${Math.abs(data.pending)}`,
    function () {
      frm.doc.custom_balance_status = "Applied";
      frm.refresh();
      frm.dirty();
      frm.save_or_update();
    }
  );
}

function show_approve_delivery_confirm_dialog(frm, data) {
  frappe.confirm(
    `Are you sure? This will allow delivery. <br/>Customer Balance: ${Math.abs(
      data.balance
    )} <br/>Sales Order Amount: ${Math.abs(
      data.total
    )} <br/>Sales Order Paid: ${Math.abs(
      data.total - data.pending
    )} <br/>Amount Pending: ${Math.abs(data.pending)}`,
    function () {
      frm.doc.custom_balance_status = "Approved";
      frm.refresh();
      frm.dirty();
      frm.save_or_update();
    }
  );
}

frappe.ui.form.on("Sales Order Item", {
  item_code: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (frm.doc.set_warehouse) {
      if (row.item_code) {
        update_warehouse_balance(frm, row);
      }
    }
  },
});

function update_warehouse_balance(frm, row) {
  frappe.call({
    method: "erpnext.stock.dashboard.item_dashboard.get_data",
    args: {
      item_code: row.item_code,
      start: 0,
    },
    callback: function (r) {
      if (r.message && r.message.length > 0) {
        r.message.map((item) => {
          if (item.warehouse == frm.doc.set_warehouse) {
            row.balance_quantity = item.actual_qty;
          } else {
            row.balance_quantity = "Unknown";
          }
        });
      }
      frm.refresh_field("items");
    },
  });
}
