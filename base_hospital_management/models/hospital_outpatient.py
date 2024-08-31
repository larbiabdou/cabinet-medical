# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Subina P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import base64
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HospitalOutpatient(models.Model):
    """Class holding Outpatient details"""
    _name = 'hospital.outpatient'
    _description = 'Hospital Outpatient'
    _rec_name = 'op_reference'
    _inherit = 'mail.thread'
    _order = 'op_date desc'

    op_reference = fields.Char(string="OP Reference", readonly=True,
                               default='New',
                               help='Op reference number of the patient')
    patient_id = fields.Many2one('res.partner',
                                 domain=[('patient_seq', 'not in',
                                          ['New', 'Employee', 'User'])],
                                 string='Patient ID', help='Id of the patient',
                                 required=True)
    is_diabetic = fields.Boolean(
        string='Diabétique',
        related="patient_id.is_diabetic",
        store="True",
        required=False)
    is_hta = fields.Boolean(
        string='HTA',
        related="patient_id.is_hta",
        store="True",
        required=False)
    is_divers = fields.Boolean(
        string='Divers',
        related="patient_id.is_divers",
        store="True",
        required=False)
    doctor_id = fields.Many2one('doctor.allocation',
                                string='Doctor',
                                help='Select the doctor',
                                domain=[('slot_remaining', '>', 0),
                                        ('date', '=', fields.date.today()),
                                        ('state', '=', 'confirm')])
    op_date = fields.Datetime(default=lambda self: fields.Datetime.now(), string='Date',
                          help='Date of OP')

    reason = fields.Text(string='Reason', help='Reason for visiting hospital')
    test_count = fields.Integer(string='Test Created',
                                help='Number of tests created for the patient',
                                compute='_compute_test_count')
    test_ids = fields.One2many('lab.test.line', 'op_id',
                               string='Tests',
                               help='Tests for the patient')
    state = fields.Selection(
        [('draft', 'Draft'), ('op', 'OP')],
        default='draft', string='State', help='State of the outpatient')
    prescription_ids = fields.One2many('prescription.line',
                                       'outpatient_id',
                                       string='Prescription',
                                       help='Prescription for the patient')
    invoiced = fields.Boolean(default=False, string='Invoiced',
                              help='True for invoiced')
    invoice_id = fields.Many2one('account.move', copy=False,
                                 string='Invoice',
                                 help='Invoice of the patient')
    attachment_id = fields.Many2one('ir.attachment',
                                    string='Attachment',
                                    help='Attachments related to the'
                                         ' outpatient')
    active = fields.Boolean(string='Active', help='True for active patients',
                            default=True)
    slot = fields.Float(string='Slot', help='Slot for the patient',
                        copy=False, readonly=True)
    is_sale_created = fields.Boolean(string='Sale Created',
                                     help='True if sale order created')
    
    note = fields.Text(
        string="Note",
        required=False)
    
    amount = fields.Float(
        string='Montant à payer', 
        required=False)
    
    amount_paid = fields.Float(
        string='Montant payé',
        tracking=True,
        required=False)
    
    payment_state = fields.Selection(
        string='Paiment_state',
        selection=[('not_paid', 'Non payé'),
                   ('in_payment', 'En paiement'),
                   ('paid', 'Payé'),],
        default='not_paid',
        tracking=True,
        required=False, )
        
    @api.onchange('amount_paid', 'amount')
    def _onchange_amount_paid(self):
        for record in self:
            if record.amount > 0:
                if record.amount_paid >= record.amount:
                    record.payment_state = 'paid'
                elif record.amount_paid > 0:
                    record.payment_state = 'in_payment'
                else:
                    record.payment_state = 'not_paid'

    medical_care_ids = fields.One2many(
        comodel_name='medical.care',
        inverse_name='outpatient_id',
        string='Soins',
        required=False)

    visit_type_id = fields.Many2one(
        comodel_name='visit.type',
        string='Type de visite',
        required=False)

    test_lab_ids = fields.One2many(
        comodel_name='laboratory.test.line',
        inverse_name='outpatient_id',
        string='Test_lab_ids',
        required=False)

    test_lab_group_ids = fields.Many2many(
        comodel_name='laboratory.test.group',
        string='Groupe de tests')

    button_consume_visible = fields.Boolean(
        string='button_consume_visible',
        compue="compute_button_consume_visible",
        required=False)

    visit_type = fields.Selection(
        string='Visit_type',
        selection=[('visit', 'Visit'),
                   ('hijama', 'hijama'),('acupuncture', 'acupuncture'),('soins', 'soins'), ],
        compute='compute_visit_type',
        store=True,
        required=False, )
    color = fields.Integer('Color', compute='_compute_color')

    def _default_has_group_doctor(self):
        if self.env.user.has_group('base_hospital_management.base_hospital_management_group_doctor'):
            return True
        else:
            return False

    has_group_doctor = fields.Boolean(
        string='Has_group_doctor',
        compute="compute_has_group_doctor",
        default=_default_has_group_doctor,
        required=False)

    def compute_has_group_doctor(self):
        for record in self:
            if self.env.user.has_group('base_hospital_management.base_hospital_management_group_doctor'):
                record.has_group_doctor = True
            else:
                record.has_group_doctor = False

    def _compute_color(self):
        for record in self:
            if record.visit_type == 'visit':
                record.color = 2  # Vert
            elif record.visit_type == 'hijama':
                record.color = 4  # Bleu
            elif record.visit_type == 'acupuncture':
                record.color = 10
            elif record.visit_type == 'soins':
                record.color = 6

    @api.depends('visit_type_id')
    def compute_visit_type(self):
        for record in self:
            if record.visit_type_id == self.env.ref("base_hospital_management.visit_type_visite"):
                record.visit_type = 'visit'
            elif record.visit_type_id == self.env.ref("base_hospital_management.visit_type_hijama"):
                record.visit_type = 'hijama'
            elif record.visit_type_id == self.env.ref("base_hospital_management.visit_type_visit_acupuncture"):
                record.visit_type = 'acupuncture'
            elif record.visit_type_id == self.env.ref("base_hospital_management.visit_type_soins"):
                record.visit_type = 'soins'
            else:
                record.visit_type = ''

    def compute_button_consume_visible(self):
        for record in self:
            if all(line.consumed for line in record.medical_care_ids or not record.medical_care_ids):
                record.button_consume_visible = True
            else:
                record.button_consume_visible = False

    @api.onchange('test_lab_group_ids')
    def onchange_test_lab_group(self):
        for record in self:
            for group in record.test_lab_group_ids:
                for test in group.sub_tests:
                    if test._origin.id not in record.test_lab_ids.mapped('test_id').ids:
                        record.test_lab_ids = [(0, 0, {
                            'test_id': test._origin.id
                        })]

    def consume_medical_care_ids(self):
        for record in self:
            location_production = self.env['stock.location'].search([('usage', '=', 'production')])
            data = []
            for line in record.medical_care_ids.filtered(lambda l: not l.consumed):
                data.append([0, 0, {
                    'name': 'Soins médicaux visite ' + record.op_reference,
                    'product_id': line.product_id.id,
                    'product_uom': line.uom_id.id,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': location_production.id,
                    'product_uom_qty': line.quantity,
                    'quantity': line.quantity,
                }])
            pick_output = self.env['stock.picking'].create({
                #'name': 'Soins',
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': location_production.id,
                'origin': self.op_reference,
                'move_ids': data,
            })
            pick_output.button_validate()
            for line in record.medical_care_ids.filtered(lambda l: not l.consumed):
                line.consumed = True

    

    @api.onchange('visit_type_id')
    def _onchange_visit_type_id(self):
        for record in self:
            for line in record.visit_type_id.medical_care_ids:
                record.medical_care_ids = [(0, 0, {
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'quantity': line.quantity,
                })]

    @api.model
    def create(self, vals):
        """Op number generator"""
        if vals.get('op_reference', 'New') == 'New':
            last_op = self.search([
                ('doctor_id', '=', vals.get('doctor_id')),
                ('op_reference', '!=', 'New'),
            ], order='create_date desc', limit=1)
            if last_op:
                last_number = int(last_op.op_reference[2:])
                new_number = last_number + 1
                vals['op_reference'] = f'OP{str(new_number).zfill(3)}'
            else:
                vals['op_reference'] = 'OP001'
        # if self.search([
        #     ('patient_id', '=', vals['patient_id']),
        # ]):
        #     raise ValidationError(
        #         'An OP already exists for this patient under the specified '
        #         'allocation')
        return super().create(vals)

    @api.depends('test_ids')
    def _compute_test_count(self):
        """Computes the value of test count"""
        self.test_count = len(self.test_ids.ids)
    #
    # @api.onchange('op_date')
    # def _onchange_op_date(self):
    #     """Method for updating the doamil of doctor_id"""
    #     self.doctor_id = False
    #     return {'domain': {'doctor_id': [('slot_remaining', '>', 0),
    #                                      ('date', '=', self.op_date),
    #                                      ('state', '=', 'confirm'), (
    #                                          'patient_type', 'in',
    #                                          [False, 'outpatient'])]}}

    @api.model
    def action_row_click_data(self, op_reference):
        """Returns data to be displayed on clicking op row"""
        op_record = self.env['hospital.outpatient'].sudo().search(
            [('op_reference', '=', op_reference),
             ('active', 'in', [True, False])])
        op_data = [op_reference, op_record.patient_id.patient_seq,
                   op_record.patient_id.name, str(op_record.op_date),
                   op_record.slot, op_record.reason,
                   op_record.doctor_id.doctor_id.name,
                   op_record.is_sale_created]
        medicines = []
        for rec in op_record.prescription_ids:
            medicines.append(
                [rec.medicine_id.name, rec.no_intakes, rec.time, rec.note,
                 rec.quantity, rec.medicine_id.id])
        return {
            'op_data': op_data,
            'medicines': medicines
        }

    # @api.model
    # def create_medicine_sale_order(self, order_id):
    #     """Method for creating sale order for medicines"""
    #     order = self.sudo().search([('op_reference', 'ilike', order_id)])
    #     sale_order = self.env['sale.order'].sudo().create({
    #         'partner_id': order.patient_id.id,
    #     })
    #     for i in order.prescription_ids:
    #         self.env['sale.order.line'].sudo().create({
    #             'product_id': i.medicine_id.id,
    #             'product_uom_qty': i.quantity,
    #             'order': sale_order.id,
    #         })
    #         self.create_invoice()

    @api.model
    def create_file(self, rec_id):
        """Method for creating prescription"""
        record = self.env['hospital.outpatient'].sudo().browse(rec_id)
        p_list = []
        data = False
        for rec in record.prescription_ids:
            p_list.append({
                'medicine': rec.medicine_id.name,
                'intake': rec.no_intakes,
                'time': rec.time.capitalize(),
                'quantity': rec.quantity,
                'note': rec.note.capitalize() if rec.note else '',
            })
            data = {
                'datas': p_list,
                'date': record.op_date,
                'patient_name': record.patient_id.name,
                'doctor_name': record.doctor_id.doctor_id.name,
            }
        pdf = self.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'base_hospital_management.action_report_patient_prescription',
            rec_id, data=data)
        record.attachment_id = self.env['ir.attachment'].sudo().create({
            'datas': base64.b64encode(pdf[0]),
            'name': "Prescription",
            'type': 'binary',
            'res_model': 'hospital.outpatient',
            'res_id': rec_id,
        })
        return {
            'url': f'/web/content'
                   f'/{record.attachment_id.id}?download=true&amp'
                   f';access_token=',
        }

    @api.model
    def create_new_out_patient(self, kw):
        """Create out patient from receptionist dashboard"""
        if kw['id']:
            partner = self.env['res.partner'].sudo().search(
                [
                    #'|', ('barcode', '=', kw['id']),
                 ('phone', '=', kw['op_phone'])])
            self.sudo().create({
                'patient_id': partner.id,
                'op_date': kw['date'],
                'reason': kw['reason'],
                'slot': kw['slot'],
                'doctor_id': kw['doctor'],
            })

    def action_create_lab_test(self):
        """Button action for creating a lab test"""
        return {
            'name': 'Create Lab Test',
            'res_model': 'lab.test.line',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_patient_type': 'outpatient',
                'default_op_id': self.id
            }
        }

    def action_view_test(self):
        """Method for viewing all lab tests"""
        return {
            'name': 'Created Tests',
            'res_model': 'lab.test.line',
            'view_mode': 'tree,form',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [
                ('patient_type', '=', 'outpatient'),
                ('op_id', '=', self.id)
            ]
        }

    # def action_convert_to_inpatient(self):
    #     """Converts an outpatient to inpatient"""
    #     self.state = 'inpatient'
    #     return {
    #         'name': 'Convert to Inpatient',
    #         'res_model': 'hospital.inpatient',
    #         'view_mode': 'form',
    #         'target': 'current',
    #         'type': 'ir.actions.act_window',
    #         'context': {
    #             'default_patient_id': self.patient_id.id,
    #             'default_attending_doctor_id': self.doctor_id.doctor_id.id,
    #         }
    #     }
    #
    # def action_op_cancel(self):
    #     """Button action for cancelling an op"""
    #     self.state = 'cancel'

    def action_confirm(self):
        """Button action for confirming an op"""
        if self.doctor_id.latest_slot == 0:
            self.slot = self.doctor_id.work_from
        else:
            self.slot = self.doctor_id.latest_slot + self.doctor_id.time_avg
        self.doctor_id.latest_slot = self.slot
        self.state = 'op'
    #
    # def create_invoice(self):
    #     """Method for creating invoice"""
    #     self.state = 'invoice'
    #     self.invoice_id = self.env['account.move'].sudo().create({
    #         'move_type': 'out_invoice',
    #         'date': fields.Date.today(),
    #         'invoice_date': fields.Date.today(),
    #         'partner_id': self.patient_id.id,
    #         'invoice_line_ids': [(
    #             0, 0, {
    #                 'name': 'Consultation fee',
    #                 'quantity': 1,
    #                 'price_unit': self.doctor_id.doctor_id.consultancy_charge,
    #             }
    #         )]
    #     })
    #     self.invoiced = True

    # def action_view_invoice(self):
    #     """Method for viewing invoice"""
    #     return {
    #         'name': 'Invoice',
    #         'domain': [('id', '=', self.invoice_id.id)],
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'tree,form',
    #         'context': {'create': False},
    #     }

    def action_print_test_order(self):
        """Method for printing prescription"""
        data = False
        p_list = []
        for rec in self.test_lab_ids:
            datas = {
                'name': rec.test_id.name,
                'parent_id': False,
            }
            p_list.append(datas)
            if rec.test_id.sub_test_ids:
                for test in rec.test_id.sub_test_ids:
                    datas = {
                        'name': test.name,
                        'parent_id': test.id,
                    }
                    p_list.append(datas)

        data = {
            'datas': p_list,
            'date': self.op_date.strftime('%d/%m/%Y'),
            'patient_name': self.patient_id.name,
            'age': self.patient_id.age,
            'lastname': self.patient_id.lastname,
            'firstname': self.patient_id.firstname,
            # 'doctor_name': self.doctor_id.doctor_id.name,
        }
        return self.env.ref(
            'base_hospital_management.action_report_test_order'). \
            report_action(self, data=data)

    def action_print_prescription(self):
        """Method for printing prescription"""
        data = False
        p_list = []
        for rec in self.prescription_ids:
            time = dict(rec._fields['time'].selection, lang='fr_FR').get(rec.time)
            note = dict(rec._fields['note'].selection).get(rec.note)
            datas = {
                'medicine': rec.medicine_id.name,
                'forme': rec.medicine_id.forme,
                'dosage': rec.medicine_id.dosage,
                #'intake': rec.no_intakes,
                #'time': time.capitalize(),
                #'quantity': rec.quantity,
                'posologie': rec.posologie, 
                #'note': note.capitalize(),
                'qsp': rec.qsp,
            }
            p_list.append(datas)
        data = {
            'datas': p_list,
            'date': self.op_date.strftime('%d/%m/%Y'),
            'patient_name': self.patient_id.name,
            'age': self.patient_id.age,
            'lastname': self.patient_id.lastname,
            'firstname': self.patient_id.firstname,
            #'doctor_name': self.doctor_id.doctor_id.name,
        }
        return self.env.ref(
            'base_hospital_management.action_report_patient_prescription'). \
            report_action(self, data=data)
    

class VisiteType(models.Model):
    _name = 'visit.type'
    _description = 'Type de visite'

    name = fields.Char(string="Nom")

    medical_care_ids = fields.One2many(
        comodel_name='medical.care',
        inverse_name='type_id',
        string='Soins',
        required=False)


class laboratoryTestLine(models.Model):
    _name = 'laboratory.test.line'
    _description = 'laboratory Test Line'

    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='Outpatient_id',
        required=False)

    test_id = fields.Many2one(
        comodel_name='laboratory.test',
        string='Test',
        required=False)

    result = fields.Char(
        string='Résultat',
        required=False)


    

