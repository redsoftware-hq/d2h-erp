frappe.ui.form.on("Purchase Receipt", {
  onload: function (frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      // frm.set_df_property("sec_warehouse", "hidden", true);
      frm.set_df_property("items_section", "hidden", true);
      frm.set_df_property("section_break0", "hidden", true);
      frm.set_df_property("accounting_dimensions_section", "hidden", true);
      frm.set_df_property("currency_and_price_list", "hidden", true);
      frm.set_df_property("taxes_charges_section", "hidden", true);
      frm.set_df_property("taxes_section", "hidden", true);
      frm.set_df_property("totals", "hidden", true);
      frm.set_df_property("section_break_46", "hidden", true);
      frm.set_df_property("section_break_42", "hidden", true);
      frm.set_df_property("sec_tax_breakup", "hidden", true);
      frm.set_df_property("pricing_rule_details", "hidden", true);
      frm.set_df_property("raw_material_details", "hidden", true);
      frm.set_df_property("custom_section_break_fmgux", "hidden", false);
    }
  },
  validate(frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      frm.doc.items = [];
      frm.refresh_field("items");
      frm.doc.custom_item_duplicate.map((item) => {
        const new_item = frm.add_child("items");
        new_item.item_code = item.item_code;
        new_item.item_name = item.item_code;
        new_item.qty = item.qty;
        new_item.uom = item.uom;
        new_item.base_rate = item.base_rate;
        new_item.stock_uom = item.stock_uom;
        new_item.conversion_factor = item.conversion_factor;
        new_item.received_qty = item.received_qty;
        new_item.serial_no = item.serial_no;
        new_item.rejected_qty = item.rejected_qty;
        new_item.purchase_order = item.purchase_order;
      });
      frm.refresh_field("items");
    } else {
      frm.doc.custom_item_duplicate = [];
      frm.refresh_field("custom_item_duplicate");
      frm.doc.items.map((item) => {
        const new_item = frm.add_child("custom_item_duplicate");
        new_item.item_code = item.item_code;
        new_item.qty = item.qty;
        new_item.uom = item.uom;
        new_item.base_rate = item.base_rate;
        new_item.stock_uom = item.stock_uom;
        new_item.conversion_factor = item.conversion_factor;
        new_item.received_qty = item.received_qty;
        new_item.serial_no = item.serial_no;
        new_item.rejected_qty = item.rejected_qty;
        new_item.purchase_order = item.purchase_order;
      });
      frm.refresh_field("custom_item_duplicate");
    }
  },
});
