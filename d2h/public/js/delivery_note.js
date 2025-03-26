frappe.ui.form.on("Delivery Note", {
  onload: function (frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      frm.set_df_property("accounting_dimensions_section", "hidden", true);
      frm.set_df_property("currency_and_price_list", "hidden", true);
      frm.set_df_property("items_section", "hidden", true);
      frm.set_df_property("section_break_30", "hidden", true);
      frm.set_df_property("section_break_49", "hidden", true);
      frm.set_df_property("taxes_section", "hidden", true);
      frm.set_df_property("section_break_46", "hidden", true);
      frm.set_df_property("totals", "hidden", true);
      frm.set_df_property("section_break_41", "hidden", true);
      frm.set_df_property("section_break_44", "hidden", true);
      frm.set_df_property("total", "hidden", true);
      frm.set_df_property("custom_section_break_jwbcu", "hidden", false);
    }
  },
  validate(frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      frm.doc.items = [];
      frm.refresh_field("items");
      frm.doc.custom_delivery_note_item_duplicate.map((item) => {
        const new_item = frm.add_child("items");
        new_item.item_code = item.item_code;
        new_item.item_name = item.item_code;
        new_item.qty = item.qty;
        new_item.uom = item.uom;
        new_item.stock_uom = item.stock_uom;
        new_item.conversion_factor = item.conversion_factor;
        new_item.stock_qty = item.stock_qty;
        new_item.serial_no = item.serial_no;
        new_item.serial_and_batch_bundle = item.serial_and_batch_bundle;
        new_item.use_serial_batch_fields = item.use_serial_batch_fields;
      });
      frm.refresh_field("items");
    } else {
      frm.doc.custom_delivery_note_item_duplicate = [];
      frm.refresh_field("custom_delivery_note_item_duplicate");
      frm.doc.items.map((item) => {
        const new_item = frm.add_child("custom_delivery_note_item_duplicate");
        new_item.item_code = item.item_code;
        new_item.qty = item.qty;
        new_item.uom = item.uom;
        new_item.stock_uom = item.stock_uom;
        new_item.conversion_factor = item.conversion_factor;
        new_item.stock_qty = item.stock_qty;
        new_item.serial_no = item.serial_no;
        new_item.serial_and_batch_bundle = item.serial_and_batch_bundle;
        new_item.use_serial_batch_fields = item.use_serial_batch_fields;
      });
      frm.refresh_field("custom_delivery_note_item_duplicate");
    }
  },
});
