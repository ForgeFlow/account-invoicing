# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestAccountInvoiceMerge(TransactionCase):
    """
        Tests for Account Invoice Merge.
    """
    def setUp(self):
        super(TestAccountInvoiceMerge, self).setUp()
        self.par_model = self.env['res.partner']
        self.context = self.env['res.users'].context_get()
        self.inv_model = self.env['account.invoice']
        self.wiz = self.env['invoice.merge']

        self.partner1 = self._create_partner()

        self.invoice1 = self._create_invoice(self.partner1, 'A')
        self.invoice2 = self._create_invoice(self.partner1, 'B')

    def _create_partner(self):
        partner = self.par_model.create({
            'name': 'Test Partner',
            'supplier': True,
            'company_type': 'company',
        })
        return partner

    def _create_invoice(self, partner, name):
        invoice = self.inv_model.create({
            'partner_id': partner.id,
            'name': name,
        })
        return invoice

    def test_account_invoice_merge(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model='account.invoice'
        ).create({})
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertDictContainsSubset(
            {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'xml_id': 'account.action_invoice_tree1',
            },
            action,
            'There was an error and the two invoices were not merged.'
        )
