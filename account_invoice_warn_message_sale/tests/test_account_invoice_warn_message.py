# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestAccountInvoiceWarnMessageSale(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warn_msg = "Partner warning"
        self.partner = self.env["res.partner"].create(
            {
                "name": "Partner",
                "invoice_warn": "warning",
                "invoice_warn_msg": self.warn_msg,
            }
        )
        self.product = self.env.ref("product.product_product_4")
        self.product.invoice_policy = "order"

    def test_action_view_invoice_context_has_warning(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 42,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()
        sale_order._create_invoices()
        action = sale_order.action_view_invoice()
        self.assertIn("context", action)
        self.assertEqual(
            action["context"].get("default_warning_message"),
            self.warn_msg,
        )
