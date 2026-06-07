frappe.ui.form.on("Farmer", {
	state(frm) {
		if (frm.doc.state !== frm._last_state) {
			frm.set_value("district", null);
			frm.set_value("block", null);
			frm.set_value("village", null);
			frm._last_state = frm.doc.state;
		}
		frm.set_query("district", () => ({
			filters: { state: frm.doc.state || "" },
		}));
	},

	district(frm) {
		if (frm.doc.district !== frm._last_district) {
			frm.set_value("block", null);
			frm.set_value("village", null);
			frm._last_district = frm.doc.district;
		}
		frm.set_query("block", () => ({
			filters: { district: frm.doc.district || "" },
		}));
	},

	block(frm) {
		if (frm.doc.block !== frm._last_block) {
			frm.set_value("village", null);
			frm._last_block = frm.doc.block;
		}
		frm.set_query("village", () => ({
			filters: { block: frm.doc.block || "" },
		}));
		frm.set_query("cluster", () => ({
			filters: { block: frm.doc.block || "" },
		}));
	},

	refresh(frm) {
		frm.set_query("district", () => ({
			filters: { state: frm.doc.state || "" },
		}));
		frm.set_query("block", () => ({
			filters: { district: frm.doc.district || "" },
		}));
		frm.set_query("village", () => ({
			filters: { block: frm.doc.block || "" },
		}));
		frm.set_query("cluster", () => ({
			filters: { block: frm.doc.block || "" },
		}));
	},
});
