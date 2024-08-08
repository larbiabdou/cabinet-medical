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
from odoo import fields, models


class PrescriptionLine(models.Model):
    """Class holding prescription line details"""
    _name = 'prescription.line'
    _description = 'Prescription Lines'
    _rec_name = 'prescription_id'

    prescription_id = fields.Many2one('hospital.prescription',
                                      string='Prescription',
                                      help='Name of the prescription')
    medicine_id = fields.Many2one('hospital.medecin',
                                  string='Medicine', required=True,
                                  help='Medicines or vaccines')
    quantity = fields.Integer(string='Quantity',
                              help="The number of medicines for the time "
                                   "period")
    no_intakes = fields.Float(string='Intakes',
                              help="How much medicine want to take")
    qsp = fields.Char(
        string='Qsp', 
        required=False)
    posologie = fields.Char(
        string='Posologie', 
        required=False)
    date = fields.Datetime(
        string='Date',
        related='outpatient_id.op_date',
        required=False)
    time = fields.Selection(
        [('once', 'Une fois par jour'), ('twice', 'Deux fois par jour'),
         ('thrice', 'Trois fois par jour'), ('morning', 'Le matin'),
         ('noon', 'À midi'), ('evening', 'Le soir')], string='Time',

        help='The interval for medicine intake')
    note = fields.Selection(
        [('before', 'Avant les repas'), ('after', 'Après les repas')],
        string='Before/ After Food',
        help='Whether the medicine to be taken before or after food')
    inpatient_id = fields.Many2one('hospital.inpatient',
                                   string='Inpatient',
                                   help='The inpatient corresponds to the '
                                        'prescription line')
    outpatient_id = fields.Many2one('hospital.outpatient',
                                    string='Outpatient',
                                    help='The outpatient corresponds to the '
                                         'prescription line')
    res_partner_id = fields.Many2one('res.partner',
                                     string='Patient',
                                     help='The outpatient corresponds to the '
                                          'prescription line',
                                     related='outpatient_id.patient_id')
