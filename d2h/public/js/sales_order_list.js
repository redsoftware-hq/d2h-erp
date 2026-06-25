frappe.listview_settings["Sales Order"] = {
  onload: function (listview) {
    if (frappe.user.has_role("Store Dept")) {
      listview.columns = listview.columns.filter(function (col) {
        if (col.df) {
          return col.df.fieldname !== "grand_total";
        }
        return true;
      });
      listview.render_header(listview.columns);
    }
  },
};
