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

from openerp.osv import fields
from openerp.osv import osv
import calendar
from datetime import datetime
from openerp import SUPERUSER_ID

class mrp_planning_report(osv.osv):

    _name = 'mrp.planning.report'

    
    
    _columns = {
        'year': fields.selection([(str(num), str(num)) for num in range(datetime.now().year, 2100)], 'Year', required=True),
        'month': fields.selection([('01','January'),('02','February'),('03','March'),('04','April'),('05','May'),('06','June'),('07','July'),('08','August'),('09','September'),('10','October'),('11','November'),('12','December')], 'Month', translate=True, required=True),
        'products': fields.one2many('mrp.planning.report.prod', 'report_id', 'Products'),
        'boms': fields.one2many('mrp.planning.report.bom', 'report_id', 'BoM Products', readonly=True),
        'status': fields.boolean('Planning status'),
    }
    
    _order = 'month'
    
    
    _defaults = {
        'year': lambda *a: datetime.now().strftime("%Y"),
        'month': lambda *a: datetime.now().strftime("%m"),
        'status': False
    }

    def calculate_bom(self, cr, uid, ids, context=None):
        
        uom_obj = self.pool.get('product.uom')
        bom_obj = self.pool.get('mrp.bom')
        planning_report_prod = self.pool.get('mrp.planning.report.prod')
        planning_report_bom = self.pool.get('mrp.planning.report.bom')
        
        zombie_prod = planning_report_prod.search(cr, uid, [('report_id', '=', None)])
        zombie_bom = planning_report_bom.search(cr, uid, [('report_id', '=', None)])
        planning_report_prod.unlink(cr, SUPERUSER_ID, [zombie for zombie in zombie_prod], context=context)
        planning_report_bom.unlink(cr, SUPERUSER_ID, [zombie for zombie in zombie_bom], context=context)
        
        for report_id in self.browse(cr, uid, ids, context=context):
        
            duplicate = self.search(cr, uid, ['&', ('year', '=', report_id.year), ('month', '=', report_id.month), ('id', '!=', report_id.id)])
            if duplicate:
                raise osv.except_osv(('Error'), ('Report exist!!!'))
            planning_report_bom.unlink(cr, SUPERUSER_ID, [line.id for line in report_id.boms], context=context)
            if report_id.products:
                for product in report_id.products:
                    bom_id = bom_obj._bom_find(cr, uid, product.product_id.id, product.prod_uom.id)
                    if bom_id:
                        bom_point = bom_obj.browse(cr, uid, bom_id)
                        factor = uom_obj._compute_qty(cr, uid, product.prod_uom.id, product.qty, bom_point.product_uom.id)
                        boms = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty)
                        for line in boms[0]:
                            bom_line = {'product_id': line['product_id'], 'qty': line['product_qty'], 'report_id': report_id.id}
                            bom_id_in = planning_report_bom.search(cr, uid, ['&', ('product_id', '=', line['product_id']), ('report_id', '=', report_id.id),])
                            if bom_id_in:
                                for b_id in bom_id_in:
                                    sum_qty = bom_line['qty'] + planning_report_bom.read(cr, uid, b_id, ['qty'], context=context)['qty']
                                    planning_report_bom.write(cr, uid, b_id, {'qty': sum_qty})
                            else:
                                planning_report_bom.create(cr, uid, bom_line)
                        
                        
class mrp_planning_report_prod(osv.osv):

    _name = 'mrp.planning.report.prod'

    
    
    _columns = {
        'product_id': fields.many2one('product.template','Product', required=True, domain="[('supply_method','=','produce')]"),
        'qty': fields.float('Product Quantity', required=True),
        'prod_uom': fields.related('product_id', 'uom_id', type='many2one', relation='product.uom', string='UoM', store=True, invisible=True, readonly=True),
        'report_id': fields.many2one('mrp.planning.report', 'Report', invisible=True, readonly=True),
    }
    
    
class mrp_planning_report_bom(osv.osv):

    _name = 'mrp.planning.report.bom'

    
    
    _columns = {
        'product_id': fields.many2one('product.product','Product'),
        'qty': fields.float('Product Quantity'),
        'bom_uom': fields.related('product_id', 'uom_id', type='many2one', relation='product.uom', string='UoM', store=True),
        'report_id': fields.many2one('mrp.planning.report', 'Report'),
    }
    

    
    
    
    