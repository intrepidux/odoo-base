# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
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

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):

    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, auth_method='user'):
        res = super(IrHttp, cls)._authenticate(auth_method=auth_method)
        if request and request.env and request.env.user:
            logging_track = request.env['base.login.reason'].search([('user_id','=',request.env.user.id),
                                                     ('state','=','audit'),
                                                     ('logged_out','=',False)], limit=1)

            timeout = logging_track.length *60
            request.env.user._auth_timeout_check(timeout)
        return res
