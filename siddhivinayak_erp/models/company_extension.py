# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class res_company_extension(models.Model):
    _inherit = 'res.company'

    plot_no = fields.Char(string='Plot No')


    @api.model
    def create(self, vals):
        result = super(res_company_extension, self).create(vals)
        # result.chart_template_id  = self.env.ref('l10n_in.indian_chart_template_standard')

        for res in self.env['res.users'].search([('id','!=',self.env.ref('base.user_admin').id)]):
            res.write({'company_ids': [(4, result.id) ]})
            
        return result
