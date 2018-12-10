# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions

class Course(models.Model):
    _name = 'openacademy.course'
    
    name = fields.Char(string='Course Name', required=True)
    description = fields.Text(string='Description of course')
    responsible_id = fields.Many2one('res.users', ondelete='set null'
    , string='Responsible', index=True) #si se elimina al usuario este campo se cambia a null.
    sessions_ids = fields.One2many('openacademy.session','course_id',string='Sessions')


class Session(models.Model):
    _name = 'openacademy.session'
    
    name = fields.Char(string='Name of session', required=True)
    course_id = fields.Many2one('openacademy.course', ondelete='set null', string='Course')
    instructor_id = fields.Many2one('res.partner', ondelete='set null', string='Instructor', required=True, domain=['|',('instructor','=',True),('category_id.name','ilike','teach')])
    
    start_date = fields.Date(default=fields.Date.today, string='Start date')
    duration = fields.Float(digits=(6,2), help='Duration in days')
    seats = fields.Integer(string='Number of seats')  
    attendee_ids = fields.Many2many('res.partner',string='Attendess')
    taken_seats = fields.Float(string='Taken Seats', compute='_taken_seats')
    active = fields.Boolean(default=True)
    end_date = fields.Date(string='End date', store=True, compute='_get_end_date', inverse='_set_end_date')
    attendee_count = fields.Integer(string='Attendees Count', compute='_get_attendees_count', store=True)
    color = fields.Integer()

    @api.depends('seats','attendee_ids')
    def _taken_seats(self):
        for record in self:
            if not record.seats:
                record.taken_seats = 0.0
            else:
                record.taken_seats = (100.0 * len(record.attendee_ids)) / record.seats

    #Event onchange:
    @api.onchange('seats','attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            #message = 'The value ' + str(self.seats) + ' is invalid.'
            return {
                'warning':{
                    'title': 'Seats field Incorrect',
                    'message' : 'The value is invalid.'
                }
            }
        if len(self.attendee_ids) > self.seats:
            return {
                'warning':{
                    'title': 'Too many attendee',
                    'message' : 'The value is invalid.'
                }
            }
    #Add constraint
    @api.constrains('instructor_id','attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")

    @api.depends('start_date','duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue
            
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1
    
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendee_count = len(r.attendee_ids)
                
class Partner(models.Model):
    _inherit = 'res.partner'

    instructor = fields.Boolean(string='Instructor', default=False)
    session_ids = fields.Many2many('openacademy.session',string='Attended sessions', readonly=True)
