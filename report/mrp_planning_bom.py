# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
import base64
from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _

class mrp_planning_bom(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(mrp_planning_bom, self).__init__(cr, uid, name, context=context)
        self.pricelist=False
        self.quantity=[]
        self.localcontext.update({
            'time': time,
            'get_period': self._get_period,
            'get_boms': self._get_boms,
            'get_titles': self._get_titles,
        })

    def _get_titles(self, form):

        lst = [{'qty': 'BoMs sum'}]
        return lst


    def _get_period(self, form):
        period = str(form['year']+'/'+form['month'])
        return period

        
    def _get_boms(self, form):

        pool = pooler.get_pool(self.cr.dbname)
        planning = pool.get('mrp.planning.report')
        product = planning.browse(self.cr, self.uid, form['id'], context=None)
        res = []
        count = 1
        for bom_id in product.boms:
            bom = {}
            bom['product'] = bom_id.product_id.name
            bom['qty'] = bom_id.qty
            bom['count'] = count
            res.append(bom)
            count += 1
        return res
        
        
        
report_sxw.report_sxw('report.mrp.planning.bom','mrp.planning.report','addons/mrp_planning_report/report/mrp_planning_bom.rml',parser=mrp_planning_bom)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
