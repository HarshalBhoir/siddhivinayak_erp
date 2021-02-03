# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'


    bank_reference = fields.Char(copy=False)
    bank_id = fields.Many2one('res.bank', 'Bank', copy=False)
    bank_branch = fields.Char(string="Branch", copy=False)
    ifsc_code = fields.Char(string='IFSC Code', copy=False)
    total_received = fields.Monetary(compute='_payment_received_total', string="Total Payment Received")

    total_paid = fields.Monetary(compute='_payment_paid_total', string="Total Payment Paid")
    total_amount = fields.Float(string="Total Payment")
    total_amount_pending = fields.Float(compute='_calculate_total_amount_pending', string="Total Payment Pending")
    partner_optout = fields.Boolean(string="Partner Opt Out", copy=False)

    def _calculate_total_amount_pending(self):
        for res in self:
            if res.total_received and res.total_amount:
                res.total_amount_pending = res.total_amount - res.total_received
            else:
                res.total_amount_pending = 0.0

    def _payment_received_total(self):
        self.total_received = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('partner_type', '=', ('customer')),
        ]
        price_totals = self.env['account.payment'].read_group(domain, ['amount'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_received = sum(price['amount'] for price in price_totals if price['partner_id'][0] in child_ids)


    def action_customer_payment_received(self):
        self.ensure_one()
        return {
            'name': 'Customer payments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('partner_id', '=', self.id),('partner_type', '=', ('customer'))],
        }


    def _payment_paid_total(self):
        self.total_paid = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('partner_type', '=', ('supplier')),
        ]
        price_totals = self.env['account.payment'].read_group(domain, ['amount'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_paid = sum(price['amount'] for price in price_totals if price['partner_id'][0] in child_ids)


    def action_supplier_payment_paid(self):
        self.ensure_one()
        return {
            'name': 'Supplier Payments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('partner_id', '=', self.id),('partner_type', '=', ('supplier'))],
        }
