# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf
import datetime

class PrintPaymentSummary(models.TransientModel):
    _name = "print.payment.summary"
    
    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date
    
    from_date = fields.Date(string='From Date', default=_get_from_date)
    to_date = fields.Date(string='To Date', default=fields.Date.context_today)
    payment_summary_file = fields.Binary('Payment Summary Report')
    file_name = fields.Char('File Name')
    payment_report_printed = fields.Boolean('Payment Report Printed')
    
    
    def action_print_payment_detail(self,):
        
        workbook = xlwt.Workbook()
        column_heading_style = easyxf('font:height 200;font:bold True;')
          
        worksheet2 = workbook.add_sheet('Customer wise Payment Summary')
        worksheet2.write(1, 0, _('Invoice Number'), column_heading_style) 
        worksheet2.write(1, 1, _('Customer'), column_heading_style)
        worksheet2.write(1, 2, _('Invoice Date'), column_heading_style)
        worksheet2.write(1, 3, _('Paid Amount'), column_heading_style)
        worksheet2.col(0).width = 5000
        worksheet2.col(1).width = 9000
        worksheet2.col(2).width = 5000
        worksheet2.col(3).width = 5000
        worksheet2.col(3).height = 5000
        row = 2
        customer_row = 2
        for wizard in self:
            customer_payment_data = {}
            heading =  'Payment Detail Report'
            worksheet2.write_merge(0, 0, 0, 5, heading, easyxf('font:height 200; align: horiz center;pattern: pattern solid, fore_color black; \
             font: color white; font:bold True;' "borders: top thin,bottom thin"))

            payment_objs = self.env['account.payment'].search([('date','>=',wizard.from_date),
                                                               ('date','<=',wizard.to_date)]) #, ('payment_ids','!=',False)


            for customer in payment_objs:

                worksheet2.write(customer_row, 0, customer.name)
                worksheet2.write(customer_row, 1, customer.partner_id.name)
                worksheet2.write(customer_row, 2, customer.date)
                worksheet2.write(customer_row, 3, customer.amount)
                customer_row += 1
#             worksheet.write(row, 5, invoice.symbol)
              
            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.payment_summary_file = excel_file
            wizard.file_name = 'Payment Detail Report.xls'
            wizard.payment_report_printed = True
            fp.close()
            return {
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'res_model': 'print.payment.summary',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                    'target': 'new',
                       }


    def action_print_payment_summary(self,):
        
        workbook = xlwt.Workbook()
        column_heading_style = easyxf('font:height 200;font:bold True;')
          
        worksheet2 = workbook.add_sheet('Customer wise Payment Summary')
        worksheet2.write(1, 0, _('Customer'), column_heading_style)
        worksheet2.write(1, 1, _('Paid Amount'), column_heading_style)
        worksheet2.col(0).width = 9000
        worksheet2.col(1).width = 5000

        row = 2
        customer_row = 2
        for wizard in self:
            customer_payment_data = {}
            heading =  'Payment Summary Report'
            worksheet2.write_merge(0, 0, 0, 5, heading, easyxf('font:height 200; align: horiz center;pattern: pattern solid, fore_color black; \
             font: color white; font:bold True;' "borders: top thin,bottom thin"))

            payment_objs = self.env['account.payment'].search([('date','>=',wizard.from_date),
                                                               ('date','<=',wizard.to_date)]) #, ('payment_ids','!=',False)


            for customer in payment_objs:
                if customer.partner_id.name not in customer_payment_data:
                    customer_payment_data.update({customer.partner_id.name: customer.amount})
                else:
                    paid_amount_data = customer_payment_data[customer.partner_id.name] + customer.amount
                    customer_payment_data.update({customer.partner_id.name: paid_amount_data})

            for customer in customer_payment_data:
                worksheet2.write(customer_row, 0, customer)
                worksheet2.write(customer_row, 1, customer_payment_data[customer])
                customer_row += 1

              
            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.payment_summary_file = excel_file
            wizard.file_name = 'Payment Summary Report.xls'
            wizard.payment_report_printed = True
            fp.close()
            return {
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'res_model': 'print.payment.summary',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                    'target': 'new',
                       }


    # def _get_accounts(self, accounts, display_account):
    #     """ compute the balance, debit and credit for the provided accounts
    #         :Arguments:
    #             `accounts`: list of accounts record,
    #             `display_account`: it's used to display either all accounts or those accounts which balance is > 0
    #         :Returns a list of dictionary of Accounts with following key and value
    #             `name`: Account name,
    #             `code`: Account code,
    #             `credit`: total amount of credit,
    #             `debit`: total amount of debit,
    #             `balance`: total amount of balance,
    #     """

    #     account_result = {}
    #     # Prepare sql query base on selected parameters from wizard
    #     tables, where_clause, where_params = self.env[
    #         'account.move.line']._query_get()
    #     tables = tables.replace('"', '')
    #     if not tables:
    #         tables = 'account_move_line'
    #     wheres = [""]
    #     if where_clause.strip():
    #         wheres.append(where_clause.strip())
    #     filters = " AND ".join(wheres)
    #     # compute the balance, debit and credit for the provided accounts
    #     request = (
    #                 "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
    #                 " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
    #     params = (tuple(accounts.ids),) + tuple(where_params)
    #     self.env.cr.execute(request, params)
    #     for row in self.env.cr.dictfetchall():
    #         account_result[row.pop('id')] = row

    #     account_res = []
    #     for account in accounts:
    #         res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
    #         currency = account.currency_id and account.currency_id or account.company_id.currency_id
    #         res['code'] = account.code
    #         res['name'] = account.name
    #         if account.id in account_result:
    #             res['debit'] = account_result[account.id].get('debit')
    #             res['credit'] = account_result[account.id].get('credit')
    #             res['balance'] = account_result[account.id].get('balance')
    #         if display_account == 'all':
    #             account_res.append(res)
    #         if display_account == 'not_zero' and not currency.is_zero(
    #                 res['balance']):
    #             account_res.append(res)
    #         if display_account == 'movement' and (
    #                 not currency.is_zero(res['debit']) or not currency.is_zero(
    #                 res['credit'])):
    #             account_res.append(res)
    #     return account_res

    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
