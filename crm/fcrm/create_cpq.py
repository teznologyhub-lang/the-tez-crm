import frappe
import sys

def create_doctypes():
    frappe.init(site="crm.localhost")
    frappe.connect()

    try:
        # CRM Quotation Item
        if not frappe.db.exists("DocType", "CRM Quotation Item"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Quotation Item",
                "module": "FCRM",
                "custom": 0,
                "istable": 1,
                "fields": [
                    {"fieldname": "product", "fieldtype": "Link", "options": "CRM Product", "label": "Product", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "description", "fieldtype": "Text", "label": "Description", "in_list_view": 1},
                    {"fieldname": "qty", "fieldtype": "Float", "label": "Quantity", "default": "1", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "in_list_view": 1, "read_only": 1}
                ]
            })
            doc.insert()
            print("Created CRM Quotation Item")

        # CRM Quotation
        if not frappe.db.exists("DocType", "CRM Quotation"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Quotation",
                "module": "FCRM",
                "custom": 0,
                "naming_rule": "By \"Naming Series\" field",
                "autoname": "naming_series:",
                "fields": [
                    {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "CRM-QTN-.YYYY.-"},
                    {"fieldname": "customer", "fieldtype": "Link", "options": "CRM Organization", "label": "Customer / Organization", "in_list_view": 1},
                    {"fieldname": "deal", "fieldtype": "Link", "options": "CRM Deal", "label": "Deal", "in_list_view": 1},
                    {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today"},
                    {"fieldname": "valid_till", "fieldtype": "Date", "label": "Valid Till"},
                    {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nSent\nAccepted\nRejected", "label": "Status", "default": "Draft", "in_list_view": 1},
                    {"fieldname": "items_section", "fieldtype": "Section Break", "label": "Items"},
                    {"fieldname": "items", "fieldtype": "Table", "options": "CRM Quotation Item", "label": "Items"},
                    {"fieldname": "totals_section", "fieldtype": "Section Break"},
                    {"fieldname": "grand_total", "fieldtype": "Currency", "label": "Grand Total", "read_only": 1, "in_list_view": 1}
                ]
            })
            doc.insert()
            print("Created CRM Quotation")

        # CRM Sales Order Item
        if not frappe.db.exists("DocType", "CRM Sales Order Item"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Sales Order Item",
                "module": "FCRM",
                "custom": 0,
                "istable": 1,
                "fields": [
                    {"fieldname": "product", "fieldtype": "Link", "options": "CRM Product", "label": "Product", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "description", "fieldtype": "Text", "label": "Description", "in_list_view": 1},
                    {"fieldname": "qty", "fieldtype": "Float", "label": "Quantity", "default": "1", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "in_list_view": 1, "read_only": 1}
                ]
            })
            doc.insert()
            print("Created CRM Sales Order Item")

        # CRM Sales Order
        if not frappe.db.exists("DocType", "CRM Sales Order"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Sales Order",
                "module": "FCRM",
                "custom": 0,
                "naming_rule": "By \"Naming Series\" field",
                "autoname": "naming_series:",
                "fields": [
                    {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "CRM-SO-.YYYY.-"},
                    {"fieldname": "quotation", "fieldtype": "Link", "options": "CRM Quotation", "label": "Quotation"},
                    {"fieldname": "customer", "fieldtype": "Link", "options": "CRM Organization", "label": "Customer / Organization", "in_list_view": 1},
                    {"fieldname": "deal", "fieldtype": "Link", "options": "CRM Deal", "label": "Deal", "in_list_view": 1},
                    {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today"},
                    {"fieldname": "delivery_date", "fieldtype": "Date", "label": "Expected Delivery Date"},
                    {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nConfirmed\nCompleted\nCancelled", "label": "Status", "default": "Draft", "in_list_view": 1},
                    {"fieldname": "items_section", "fieldtype": "Section Break", "label": "Items"},
                    {"fieldname": "items", "fieldtype": "Table", "options": "CRM Sales Order Item", "label": "Items"},
                    {"fieldname": "totals_section", "fieldtype": "Section Break"},
                    {"fieldname": "grand_total", "fieldtype": "Currency", "label": "Grand Total", "read_only": 1, "in_list_view": 1}
                ]
            })
            doc.insert()
            print("Created CRM Sales Order")

        # CRM Invoice Item
        if not frappe.db.exists("DocType", "CRM Invoice Item"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Invoice Item",
                "module": "FCRM",
                "custom": 0,
                "istable": 1,
                "fields": [
                    {"fieldname": "product", "fieldtype": "Link", "options": "CRM Product", "label": "Product", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "description", "fieldtype": "Text", "label": "Description", "in_list_view": 1},
                    {"fieldname": "qty", "fieldtype": "Float", "label": "Quantity", "default": "1", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1, "reqd": 1},
                    {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "in_list_view": 1, "read_only": 1}
                ]
            })
            doc.insert()
            print("Created CRM Invoice Item")

        # CRM Invoice
        if not frappe.db.exists("DocType", "CRM Invoice"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "CRM Invoice",
                "module": "FCRM",
                "custom": 0,
                "naming_rule": "By \"Naming Series\" field",
                "autoname": "naming_series:",
                "fields": [
                    {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "CRM-INV-.YYYY.-"},
                    {"fieldname": "sales_order", "fieldtype": "Link", "options": "CRM Sales Order", "label": "Sales Order"},
                    {"fieldname": "customer", "fieldtype": "Link", "options": "CRM Organization", "label": "Customer / Organization", "in_list_view": 1},
                    {"fieldname": "deal", "fieldtype": "Link", "options": "CRM Deal", "label": "Deal", "in_list_view": 1},
                    {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today"},
                    {"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date"},
                    {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nUnpaid\nPaid\nOverdue\nCancelled", "label": "Status", "default": "Draft", "in_list_view": 1},
                    {"fieldname": "items_section", "fieldtype": "Section Break", "label": "Items"},
                    {"fieldname": "items", "fieldtype": "Table", "options": "CRM Invoice Item", "label": "Items"},
                    {"fieldname": "totals_section", "fieldtype": "Section Break"},
                    {"fieldname": "grand_total", "fieldtype": "Currency", "label": "Grand Total", "read_only": 1, "in_list_view": 1}
                ]
            })
            doc.insert()
            print("Created CRM Invoice")

        frappe.db.commit()
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
        frappe.db.rollback()

if __name__ == "__main__":
    create_doctypes()
