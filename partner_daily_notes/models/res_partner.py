# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartnerNotes(models.Model):
    _description = "Daily notes for a partner"
    _name = "res.partner.notes"

    name = fields.Char(string="Title")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Job seeker")

    administrative_officer = fields.Many2one(
        "res.users", string="Administrative officer", default=lambda self: self.env.user
    )
    note = fields.Text(string="Notes")
    note_date = fields.Datetime(string="Refers to date", default=fields.Datetime.now)
    is_confidential = fields.Boolean(string="Secret", help="Apply/Remove Secret")
    note_type = fields.Many2one(comodel_name="res.partner.note.type")
    note_number = fields.Char(string="AIS number")
    appointment_id = fields.Many2one(
        comodel_name="calendar.appointment", string="Linked meeting"
    )
    office_id = fields.Many2one("hr.department", string="Office")
    customer_id = fields.Char(
        string="Customer number", related="partner_id.customer_id"
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _create_next_last_msg(self):
        if self.is_jobseeker:
            route = self.env.ref(
                "edi_af_aisf_trask.asok_contact_route", raise_if_not_found=False
            )
            if route:
                vals = {
                    "name": "set contact msg",
                    "edi_type": self.env.ref("edi_af_aisf_trask.asok_contact").id,
                    "model": self._name,
                    "res_id": self.id,
                    "route_id": route.id,
                    "route_type": "edi_af_aisf_trask_contact",
                }
                message = self.env["edi.message"].create(vals)
                message.pack()

    notes_ids = fields.One2many(
        comodel_name="res.partner.notes",
        string="Daily notes",
        inverse_name="partner_id",
    )
    next_contact_date = fields.Datetime(string="Next contact")
    next_contact_time = fields.Char(string="Next contact time")
    next_contact_type = fields.Selection(
        string="Next contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
    )

    next_contact = fields.Char(string="Next contact", compute="_compute_next_contact")
    last_contact_date = fields.Datetime(string="Latest contact")
    last_contact_type = fields.Selection(
        string="Latest contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
    )

    last_contact = fields.Char(string="Latest contact", compute="_compute_last_contact")

    @api.one
    def _compute_next_contact(self):
        if self.next_contact_date:
            res = f"{self.next_contact_date.date()} {self.next_contact_time if self.next_contact_time else ''} {self.next_contact_type}"
        else:
            res = _("No next contact")
        self.next_contact = res

    @api.one
    def _compute_last_contact(self):
        if self.last_contact_date:
            res = f"{self.last_contact_date.date()} {self.last_contact_type}"
        else:
            res = _("No last contact")
        self.last_contact = res

    def action_view_next_event(self):
        action = {
            "name": _(self.name + " - notes"),
            "domain": [("partner_id", "=", self.ids)],
            "view_type": "form",
            "res_model": "res.partner.notes",
            "view_id": self.env.ref("partner_daily_notes.partner_notes_view_tree").id,
            "view_mode": "tree",
            "type": "ir.actions.act_window",
        }
        if len(self) == 1:
            action["context"] = {"default_partner_id": self.id}
        return action


class ResPartnerNoteType(models.Model):
    _name = "res.partner.note.type"
    _rec_name = "description"

    note_id = fields.One2many(
        comodel_name="res.partner.notes", inverse_name="note_type"
    )
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
