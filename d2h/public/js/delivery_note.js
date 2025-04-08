frappe.ui.form.on("Delivery Note", {
  refresh: function (frm) {
    frm.fields_dict["custom_delivery_note_item_duplicate"].grid.wrapper.on(
      "change",
      'input[data-fieldname="qty"]',
      function () {
        roles = frappe.user_roles;
        if (roles.includes("Store Dept") && !roles.includes("Administrator")) {
          frm.doc.custom_item_duplicate.map((item) => {
            frm.doc.items.map((new_item) => {
              if (new_item.item_code == item.item_code) {
                new_item.qty = item.qty;
              }
            });
          });
          frm.refresh_field("items");
        }
      }
    );
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      if (
        frm.doc.items &&
        frm.doc.custom_delivery_note_item_duplicate &&
        !compareListsByKey(
          frm.doc.items,
          frm.doc.custom_delivery_note_item_duplicate,
          "item_code"
        )
      ) {
        update_duplicate_items(frm);
      }
    }
  },
  validate(frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      if (
        frm.doc.items &&
        frm.doc.custom_delivery_note_item_duplicate &&
        frm.doc.custom_delivery_note_item_duplicate.length <
          frm.doc.items.length
      ) {
        const availableIdx = new Set(
          frm.doc.custom_delivery_note_item_duplicate.map((item) => item.idx)
        );
        frm.doc.items = frm.doc.items.filter((item) =>
          availableIdx.has(item.idx)
        );
      }
    }
  },
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
    frm.fields_dict["custom_delivery_note_item_duplicate"].grid.wrapper
      .find(".grid-add-row")
      .hide();

    frm.fields_dict[
      "custom_delivery_note_item_duplicate"
    ].grid.cannot_add_rows = true;
    frm.fields_dict[
      "custom_delivery_note_item_duplicate"
    ].grid.only_sortable = false;

    frm.fields_dict["custom_delivery_note_item_duplicate"].grid.refresh();
  },
});

frappe.ui.form.on("Delivery Note Item", {
  item_code: function (frm, cdt, cdn) {
    update_duplicate_items(frm);
  },
});

function update_duplicate_items(frm, row) {
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

function compareListsByKey(list1, list2, key) {
  if (list1.length !== list2.length) return false;

  for (let i = 0; i < list1.length; i++) {
    if (list1[i][key] !== list2[i][key]) {
      return false;
    }
  }

  return true;
}
