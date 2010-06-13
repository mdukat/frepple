#
# Copyright (C) 2007-2010 by Johan De Taeye
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

# file : $URL$
# revision : $LastChangedRevision$  $LastChangedBy$
# date : $LastChangedDate$

from django.test import TestCase

from freppledb.input.models import *

class OutputTest(TestCase):

  def setUp(self):
    # Login
    self.client.login(username='frepple', password='frepple')

  # Buffer
  def test_output_buffer(self):
    response = self.client.get('/buffer/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, '8 buffers')

  def test_output_buffer_csvtable(self):
    response = self.client.get('/buffer/', {'reporttype':'csv'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  def test_output_buffer_csvlist(self):
    response = self.client.get('/buffer/', {'reporttype':'csvlist'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  # Resource
  def test_output_resource(self):
    response = self.client.get('/resource/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, '3 resources')

  def test_output_resource_csvtable(self):
    response = self.client.get('/resource/', {'reporttype':'csv'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  # Demand
  def test_output_demand(self):
    response = self.client.get('/demand/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, 'Demand report')

  def test_output_demand_csvlist(self):
    response = self.client.get('/demand/', {'reporttype':'csvlist'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  # Forecast
  def test_output_forecast(self):
    response = self.client.get('/forecast/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, '2 forecasts')

  def test_output_forecast_csvlist(self):
    response = self.client.get('/forecast/', {'reporttype':'csvlist'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  # Operation
  def test_output_operation(self):
    response = self.client.get('/operation/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, '14 operations')

  def test_output_operation_csvtable(self):
    response = self.client.get('/operation/', {'reporttype':'csv'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')

  # Problem
  def test_output_problem(self):
    response = self.client.get('/problem/')
    self.failUnlessEqual(response.status_code, 200)
    self.assertContains(response, '0 problems')

  def test_output_problem_csvlist(self):
    response = self.client.get('/problem/', {'reporttype':'csvlist'})
    self.failUnlessEqual(response.status_code, 200)
    self.failUnlessEqual(response.__getitem__('Content-Type'), 'text/csv')
