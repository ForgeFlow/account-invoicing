# -*- coding: utf-8 -*-
# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright (c) 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_invoice_key_cols(self):
        return super(AccountInvoice, self)._get_invoice_key_cols() + [
            'payment_mode_id',
        ]

    @api.model
    def _get_first_invoice_fields(self, invoice):
        res = super(AccountInvoice, self)._get_first_invoice_fields(invoice)
        res.update({'payment_mode_id': invoice.payment_mode_id.id})
        return res
