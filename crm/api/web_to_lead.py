import json
import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def submit_web_lead(form_id=None, **kwargs):
	"""
	Public endpoint for receiving web-to-lead submissions.
	Supports both JSON body and form-encoded data.
	"""
	# Handle parameters passed as form body, query params, or payload kwarg
	if not form_id:
		form_id = kwargs.get("form_id") or frappe.form_dict.get("form_id")

	if not form_id:
		frappe.local.response["http_status_code"] = 400
		return {"status": "error", "message": _("Missing form_id parameter")}

	if not frappe.db.exists("CRM Web Form", form_id):
		frappe.local.response["http_status_code"] = 444
		return {"status": "error", "message": _("Invalid or inactive form ID")}

	form_doc = frappe.get_doc("CRM Web Form", form_id)

	if not form_doc.is_active:
		frappe.local.response["http_status_code"] = 403
		return {"status": "error", "message": _("This web form is currently disabled.")}

	# Extract form values from kwargs, frappe.form_dict, or request body
	data = dict(kwargs)
	if frappe.request and frappe.request.data:
		try:
			body_json = json.loads(frappe.request.data.decode("utf-8"))
			if isinstance(body_json, dict):
				data.update(body_json)
		except Exception:
			pass

	# Include frappe.form_dict
	for k, v in frappe.form_dict.items():
		if k not in ("cmd", "form_id"):
			data[k] = v

	# Validate required fields
	missing_fields = []
	for field in form_doc.fields:
		if field.reqd and not data.get(field.fieldname):
			missing_fields.append(field.label or field.fieldname)

	if missing_fields:
		frappe.local.response["http_status_code"] = 400
		return {
			"status": "error",
			"message": _("Please fill in required fields: {0}").format(", ".join(missing_fields)),
		}

	# Map data to CRM Lead attributes
	first_name = data.get("first_name") or ""
	last_name = data.get("last_name") or ""
	full_name = data.get("lead_name") or data.get("name") or f"{first_name} {last_name}".strip()
	email = data.get("email") or data.get("email_id") or ""
	phone = data.get("phone") or data.get("mobile_no") or data.get("mobile") or ""
	organization = data.get("organization") or data.get("company") or ""
	message = data.get("message") or data.get("notes") or data.get("comments") or ""

	if not full_name:
		full_name = email or phone or "Web Lead"

	lead_dict = {
		"doctype": "CRM Lead",
		"lead_name": full_name,
		"email_id": email,
		"mobile_no": phone,
		"organization": organization,
		"source": form_doc.lead_source or "Web Form",
		"lead_owner": form_doc.default_lead_owner or None,
	}

	# Collect extra fields into notes
	extra_notes = []
	if message:
		extra_notes.append(f"<b>Message:</b> {message}")

	known_fields = {"first_name", "last_name", "lead_name", "name", "email", "email_id", "phone", "mobile_no", "mobile", "organization", "company", "message", "notes", "comments", "cmd", "form_id"}
	for k, v in data.items():
		if k not in known_fields and v:
			extra_notes.append(f"<b>{k.replace('_', ' ').title()}:</b> {v}")

	if extra_notes:
		lead_dict["notes"] = "<br>".join(extra_notes)

	try:
		# Create Lead ignoring user permissions since guest submits
		lead = frappe.get_doc(lead_dict)
		lead.insert(ignore_permissions=True)
		frappe.db.commit()

		# Trigger Frappe doc event for Workflow Rules if active
		frappe.get_doc("CRM Lead", lead.name).run_method("after_insert")

		return {
			"status": "success",
			"message": form_doc.success_message or _("Thank you! Your submission has been received."),
			"redirect_url": form_doc.redirect_url or None,
			"lead": lead.name,
		}

	except Exception as e:
		frappe.log_error("Web-to-Lead Error", str(e))
		frappe.local.response["http_status_code"] = 500
		return {"status": "error", "message": _("An error occurred while submitting your form. Please try again.")}


@frappe.whitelist(allow_guest=True)
def get_form_config(form_id):
	"""Returns form structure for embedding dynamically via JS script."""
	if not frappe.db.exists("CRM Web Form", form_id):
		frappe.throw(_("Form not found"))

	doc = frappe.get_doc("CRM Web Form", form_id)
	return {
		"name": doc.name,
		"title": doc.title,
		"is_active": doc.is_active,
		"success_message": doc.success_message,
		"fields": [
			{
				"fieldname": f.fieldname,
				"label": f.label,
				"fieldtype": f.fieldtype,
				"reqd": f.reqd,
				"placeholder": f.placeholder,
				"options": f.options.split("\n") if f.options else [],
			}
			for f in doc.fields
		],
	}


@frappe.whitelist()
def get_web_forms():
	"""Fetch list of all web forms for management UI."""
	forms = frappe.get_all(
		"CRM Web Form",
		fields=["name", "title", "is_active", "lead_source", "default_lead_owner", "creation", "modified"],
		order_by="creation desc",
	)

	# Attach submission counts
	for f in forms:
		f["submissions_count"] = frappe.db.count("CRM Lead", filters={"source": f.get("lead_source") or "Web Form"})
		f["fields"] = frappe.get_all(
			"CRM Web Form Field",
			filters={"parent": f["name"]},
			fields=["fieldname", "label", "fieldtype", "reqd", "placeholder", "options"],
		)

	return forms


@frappe.whitelist()
def save_web_form(form_data):
	"""Create or update a web form."""
	if isinstance(form_data, str):
		form_data = json.loads(form_data)

	name = form_data.get("name")
	if name and frappe.db.exists("CRM Web Form", name):
		doc = frappe.get_doc("CRM Web Form", name)
		doc.update(form_data)
	else:
		doc = frappe.get_doc({
			"doctype": "CRM Web Form",
			"title": form_data.get("title", "New Web Form"),
			"is_active": form_data.get("is_active", 1),
			"lead_source": form_data.get("lead_source", "Web Form"),
			"default_lead_owner": form_data.get("default_lead_owner"),
			"success_message": form_data.get("success_message", "Thank you! We will get back to you soon."),
			"redirect_url": form_data.get("redirect_url"),
			"fields": form_data.get("fields", []),
		})

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.as_dict()


@frappe.whitelist()
def delete_web_form(name):
	"""Delete a web form."""
	frappe.delete_doc("CRM Web Form", name, ignore_permissions=True)
	frappe.db.commit()
	return True


@frappe.whitelist()
def get_embed_code(form_id):
	"""Generates HTML snippet and script embeds for a given form."""
	site_url = frappe.utils.get_url()
	api_url = f"{site_url}/api/method/crm.api.web_to_lead.submit_web_lead"

	doc = frappe.get_doc("CRM Web Form", form_id)

	# Generate raw HTML form snippet
	field_inputs = []
	for f in doc.fields:
		req_attr = "required" if f.reqd else ""
		ph_attr = f'placeholder="{f.placeholder}"' if f.placeholder else ""
		req_star = " *" if f.reqd else ""
		
		if f.fieldtype in ("Small Text", "Text"):
			input_html = f'<textarea name="{f.fieldname}" class="tez-input" {ph_attr} {req_attr} rows="3"></textarea>'
		elif f.fieldtype == "Select" and f.options:
			opt_items = [f'<option value="{opt.strip()}">{opt.strip()}</option>' for opt in f.options.split("\n") if opt.strip()]
			opts = "".join(opt_items)
			input_html = f'<select name="{f.fieldname}" class="tez-input" {req_attr}><option value="">-- Select --</option>{opts}</select>'
		else:
			is_email = "email" in (f.fieldname or "")
			is_phone = "phone" in (f.fieldname or "") or f.fieldtype == "Phone"
			input_type = "email" if is_email else ("tel" if is_phone else "text")
			input_html = f'<input type="{input_type}" name="{f.fieldname}" class="tez-input" {ph_attr} {req_attr} />'

		field_inputs.append(f"""
  <div class="tez-form-group">
    <label class="tez-label">{f.label}{req_star}</label>
    {input_html}
  </div>""")

	raw_html = f"""<!-- TezCRM Web-to-Lead Form: {doc.title} -->
<form id="tez-web-form-{form_id}" action="{api_url}" method="POST" class="tez-web-form">
  <input type="hidden" name="form_id" value="{form_id}" />
  <h3 class="tez-form-title">{doc.title}</h3>
  {"".join(field_inputs)}
  <button type="submit" class="tez-submit-btn">Submit</button>
  <div id="tez-form-status-{form_id}" class="tez-form-status"></div>
</form>

<style>
.tez-web-form {{ max-width: 480px; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; font-family: system-ui, -apple-system, sans-serif; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
.tez-form-title {{ margin-top: 0; margin-bottom: 20px; font-size: 20px; font-weight: 700; color: #0f172a; }}
.tez-form-group {{ margin-bottom: 16px; text-align: left; }}
.tez-label {{ display: block; font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 6px; }}
.tez-input {{ width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; transition: border-color 0.2s; }}
.tez-input:focus {{ outline: none; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }}
.tez-submit-btn {{ width: 100%; padding: 12px; font-size: 15px; font-weight: 600; color: #ffffff; background-color: #4f46e5; border: none; border-radius: 6px; cursor: pointer; transition: background-color 0.2s; }}
.tez-submit-btn:hover {{ background-color: #4338ca; }}
.tez-form-status {{ margin-top: 14px; font-size: 14px; text-align: center; }}
.tez-status-success {{ color: #16a34a; font-weight: 600; }}
.tez-status-error {{ color: #dc2626; font-weight: 600; }}
</style>

<script>
document.getElementById('tez-web-form-{form_id}').addEventListener('submit', function(e) {{
  e.preventDefault();
  var form = this;
  var statusDiv = document.getElementById('tez-form-status-{form_id}');
  var btn = form.querySelector('.tez-submit-btn');
  btn.disabled = true;
  btn.innerText = 'Submitting...';

  var formData = new FormData(form);
  fetch(form.action, {{
    method: 'POST',
    body: formData
  }})
  .then(function(res) {{ return res.json(); }})
  .then(function(res) {{
    var data = res.message || res;
    if (data.status === 'success') {{
      statusDiv.className = 'tez-form-status tez-status-success';
      statusDiv.innerText = data.message;
      form.reset();
      if (data.redirect_url) setTimeout(function() {{ window.location.href = data.redirect_url; }}, 2000);
    }} else {{
      statusDiv.className = 'tez-form-status tez-status-error';
      statusDiv.innerText = data.message || 'Submission failed.';
    }}
  }})
  .catch(function(err) {{
    statusDiv.className = 'tez-form-status tez-status-error';
    statusDiv.innerText = 'Network error. Please try again.';
  }})
  .finally(function() {{
    btn.disabled = false;
    btn.innerText = 'Submit';
  }});
}});
</script>
"""

	return {
		"raw_html": raw_html,
		"api_endpoint": api_url,
		"form_id": form_id,
	}
