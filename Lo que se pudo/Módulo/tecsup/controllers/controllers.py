# -*- coding: utf-8 -*-
from odoo import http

class Tecsup(http.Controller):
    @http.route('/academy/courses/all/', auth='public', website= True)
    def index(self, **kw):
        courses = http.request.env['openacademy.course'].search([])
        return http.request.render('tecsup.courses_list', {
            'courses': courses,
        })

    @http.route('/academy/sessions/all/', auth='public', website= True)
    def list(self, **kw):
        return http.request.render('tecsup.sessions_list', {
            'sessions': http.request.env['openacademy.session'].search([]),
        })

#     @http.route('/tecsup/tecsup/objects/<model("tecsup.tecsup"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tecsup.object', {
#             'object': obj
#         })