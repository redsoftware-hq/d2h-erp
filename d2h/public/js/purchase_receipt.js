frappe.ui.form.on("Purchase Receipt", {
  onload: function (frm) {
    if (
      frappe.user_roles.includes("Store Dept") &&
      !frappe.user_roles.includes("Administrator")
    ) {
      frm.set_df_property("sec_warehouse", "hidden", true);
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
});
