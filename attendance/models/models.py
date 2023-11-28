# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime


class attendance(models.Model):
    _name = 'attendance.attendance'
    _description = 'attendance.attendance'

    sequence = fields.Char(string='Order Reference', copy=False, inedx=True,
                           readonly=False, default=lambda self: ('New'))
    employee = fields.Many2one('hr.employee', string='Employee')
    requested = fields.Date(default=date.today(), string="Date")
    type = fields.Selection(
        [('1', 'check in'), ('2', 'check out'), ('3', 'both')], string='Type'
    )
    reason = fields.Text()
    action = fields.Selection(
        [('1', 'New Record'), ('2', 'Modification')], string="Action To Do"
    )
    attendance = fields.Text(string="Attendance", readonly=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting', 'Waiting For Approve'), ('approve', 'Approve')],
        default='draft'
    )

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'attendance.Sequence') or 'New'
        res = super(attendance, self).create(vals)
        return res

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_done(self):
        for rec in self:
            rec.state = 'waiting'

    def action_cancel(self):
        for rec in self:
            rec.state = 'approve'

    def action_Confirm(self):
         template = self.env.ref('attendance.mail_template')
         for rec in self:
             template.send_mail(rec.id)
        for rec in self:
            rec.state = 'waiting'

    @api.onchange('action')
    def test(self):
        for record in self:
            if record.action == '2':
                field = self.env['hr.attendance'].search([])
                name = self.env.user.name
                for rec in field:
                    record.attendance = f'{name} form {rec.check_in} to {rec.check_out}'
            else:
                record.attendance = " "
