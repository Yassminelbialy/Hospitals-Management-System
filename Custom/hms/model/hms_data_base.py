from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

import re

class Patient(models.Model):
    _rec_name = "first_name"
    _name = "hms.patient"

    blood_type = fields.Selection([('a', 'a'), ('b', 'b'), ('o', 'o')])
    department_capacity = fields.Integer(related="department_id.capacity")
    first_name = fields.Char()
    birth_date = fields.Date()
    age = fields.Integer(compute="compute_age")
    email=fields.Char();
    last_name = fields.Char()
    cr_ratio = fields.Float()
    address = fields.Char()
    history = fields.Html()
    image = fields.Binary()
    email = fields.Char()
    pcr = fields.Boolean()
    state = fields.Selection([
        ('Undetermined', 'Undetermined'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Serious', 'Serious'),
    ], default="Undetermined")
    department_id = fields.Many2one("hms.department")
    doctor_id = fields.Many2many("hms.doctor")
    log_ids = fields.One2many("hms.patient_log", "patient_id")
    # Computer age from birth day
    @api.multi
    @api.depends('birth_date')
    def compute_age(self):
         for record in self:
              age = relativedelta(datetime.now().date(), fields.Datetime.from_string(record.birth_date)).years
              record.age = age
    # Change patient state
    def change_state(self):
        if self.state == "Undetermined":
            self.state = "Good"
        elif self.state == "Good":
            self.state = "Fair"
        elif self.state == "Fair":
            self.state = "Serious"

        self.log_ids.create({"updates": f"State changed to {self.state}", "patient_id": self.id})

    @api.onchange('age')
    def change_age(self):
        if self.age < 30:
            self.pcr = True
            return {"warning": {"title": "PCR", "message": "the pcr is now checked"}}

    @api.constrains('email')
    def validate_email(self):
         for obj in self:
               if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", obj.email) == None:
                   raise ValidationError("Please Provide valid Email Address: %s" % obj.email)

    _sql_constraints = [('dulicated email','UNIQUE (email)','email all already exists') ]
class PatientLog(models.Model):
    _name = "hms.patient_log"

    updates = fields.Text()
    time = fields.Datetime(default=datetime.today())

    current_user = fields.Many2one('res.users', 'by User', default=lambda self: self.env.user.id, readonly=True)
    patient_id = fields.Many2one("hms.patient")

    @api.model
    def create(self, values):
        new_record = super().create(values)
        return new_record
