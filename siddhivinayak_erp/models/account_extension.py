# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    qty = fields.Char(string="Quantity")
    rate = fields.Float(string="Rate")
    material_type = fields.Char(string="Material Type", copy=False)

    plot_no = fields.Char(string='Plot No', related='company_id.plot_no')
    effective_date = fields.Date('Effective Date',
                                 help='Effective date of PDC', copy=False)
    bank_reference = fields.Char(copy=False)
    bank_id = fields.Many2one('res.bank', 'Bank', copy=False)
    bank_branch = fields.Char(string="Branch", copy=False)
    ifsc_code = fields.Char(string="IFSC Code", copy=False)
    cheque_reference = fields.Char(string="Payment/Cheque Ref", copy=False)
    journal_type = fields.Selection([
            ('sale', 'Sales'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ],string="Journal Type")
    company_id = fields.Many2one('res.company', 'Company',
            default=lambda self: self.env.company, ondelete='cascade', readonly=False)

    gst_tax_ids = fields.Many2many('account.tax', 'gst_tax_ids_rel', string='GST Taxes', check_company=True)
    non_gst_tax_ids = fields.Many2many('account.tax', 'non_gst_tax_ids_rel', string='Non GST Taxes', check_company=True)
    amount_without_gst = fields.Float(string="Amount without GST")
    gst_tax_amount = fields.Float(string="GST Tax Amount")
    non_gst_tax_amount = fields.Float(string="Non GST Tax Amount")

    date = fields.Date(string='Challan Date', required=True, index=True, readonly=True,
        states={'draft': [('readonly', False)]}, copy=False, default=fields.Date.context_today )

    payment_date = fields.Date(string='Date', required=True, index=True, readonly=True,
        states={'draft': [('readonly', False)]}, copy=False, default=fields.Date.context_today )

    @api.onchange('qty')
    def check_numeric(self):
        if self.qty:
            try:
               test = float(self.qty)
            except:
                return {'warning':{'title':'Validation Error','message':'Quantity should be numeric'}}

    @api.depends('qty','rate')
    @api.onchange('qty','rate')
    def onchange_rate_qty(self):
        if self.qty and self.rate:
            self.amount_without_gst = float(self.qty) * self.rate


    @api.onchange('partner_id')
    def onchange_partner_id_sv(self):
        if self.partner_id:
            self.bank_reference = self.partner_id.bank_reference
            self.bank_id = self.partner_id.bank_id.id
            self.bank_branch = self.partner_id.bank_branch
            self.ifsc_code = self.partner_id.ifsc_code
        else:
            self.bank_reference = False
            self.bank_id = False
            self.bank_branch = False
            self.ifsc_code = False


    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.journal_type = self.journal_id.type
        else:
            self.journal_type = False


    @api.depends('company_id')
    @api.onchange('company_id')
    def onchange_company_id(self):
        for rec in self:
            if rec.partner_type == 'customer':
                type_tax_use = 'sale'
            elif rec.partner_type == 'supplier':
                type_tax_use = 'purchase'

            return  {'domain':
                            {'gst_tax_ids':[('company_id', '=', rec.company_id.id),
                                            ('type_tax_use', '=', type_tax_use)],
                            'non_gst_tax_ids': [('company_id', '=', rec.company_id.id),
                                                ('type_tax_use', '=', type_tax_use)]}
                    }


    @api.depends('amount_without_gst', 'gst_tax_ids', 'non_gst_tax_ids')
    @api.onchange('amount_without_gst', 'gst_tax_ids', 'non_gst_tax_ids')
    def onchange_amount_untaxed(self):
        gst_tax_amount= non_gst_tax_amount=0.0

        if self.amount_without_gst:
            amount = self.amount_without_gst

            if self.gst_tax_ids:
                for tax in [x.amount for x in self.gst_tax_ids]:
                    gst_tax_amount += (tax/100)*amount

            if self.non_gst_tax_ids:
                for tax2 in [x.amount for x in self.non_gst_tax_ids]:
                    non_gst_tax_amount += (tax2/100)*amount

            self.gst_tax_amount = gst_tax_amount
            self.non_gst_tax_amount = non_gst_tax_amount
            self.amount = amount + gst_tax_amount + non_gst_tax_amount


class ResPartnerBankInherit(models.Model):
    _inherit = 'res.partner.bank'

    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade', readonly=False)
    ifsc_code = fields.Char(string="IFSC Code")


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    company_id = fields.Many2one('res.company', 'Company',
            default=lambda self: self.env.company, ondelete='cascade', readonly=False)

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    company_id = fields.Many2one('res.company', 'Company',
            default=lambda self: self.env.company, ondelete='cascade', readonly=False)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    gst_type = fields.Selection([('GST', 'GST'), ('Non GST', 'Non GST')], string="GST Type")
