from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class crm_db(models.Model):
    _inherit = 'res.partner'
    related_patient_id=fields.Many2one("hms.patient")
    vat=fields.Char(required=True,readonly=False)

    @api.multi
    def unlink(self):
        if self.related_patient_id:
            raise ValidationError('this customer is linked with a patient')
        else:
            super().unlink()

#Email Validtion
