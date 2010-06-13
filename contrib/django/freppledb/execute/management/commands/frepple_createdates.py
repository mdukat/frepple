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

#  file     : $URL$
#  revision : $LastChangedRevision$  $LastChangedBy$
#  date     : $LastChangedDate$

import random
from optparse import make_option
from datetime import timedelta, datetime, date

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, DEFAULT_DB_ALIAS, transaction
from django.conf import settings
from django.utils.translation import ugettext as _

from freppledb.input.models import *
from freppledb.execute.models import log


class Command(BaseCommand):

  help = '''
  This command initiliazes the date bucketization table in the database.
  '''

  option_list = BaseCommand.option_list + (
      make_option('--start', dest='start', type='string',
          help='Start date in YYYY-MM-DD format'),
      make_option('--end', dest='end', type='string',
          help='End date in YYYY-MM-DD format'),
      make_option('--user', dest='user', type='string',
          help='User running the command'),
      make_option('--nonfatal', action="store_true", dest='nonfatal', 
        default=False, help='Dont abort the execution upon an error'),
      make_option('--database', action='store', dest='database',
        default=DEFAULT_DB_ALIAS, help='Nominates a specific database to populate date information into'),
  )

  requires_model_validation = False

  def get_version(self):
    return settings.FREPPLE_VERSION


  def handle(self, **options):
    # Make sure the debug flag is not set!
    # When it is set, the django database wrapper collects a list of all sql
    # statements executed and their timings. This consumes plenty of memory
    # and cpu time.
    tmp_debug = settings.DEBUG
    settings.DEBUG = False

    # Pick up the options
    if 'start' in options: start = options['start'] or '2008-1-1'
    else: start = '2008-1-1'
    if 'end' in options: end = options['end'] or '2012-1-1'
    else: end = '2012-1-1'
    if 'user' in options: user = options['user'] or ''
    else: user = ''
    nonfatal = False
    if 'nonfatal' in options: nonfatal = options['nonfatal']
    if 'database' in options: database = options['database'] or DEFAULT_DB_ALIAS
    else: database = DEFAULT_DB_ALIAS      
    if not database in settings.DATABASES.keys():
      raise CommandError("No database settings known for '%s'" % database )

    # Validate the date arguments
    try:
      curdate = datetime.strptime(start,'%Y-%m-%d')
      end = datetime.strptime(end,'%Y-%m-%d')
    except Exception, e:
      raise CommandError("Date is not matching format YYYY-MM-DD")

    transaction.enter_transaction_management(using=database)
    transaction.managed(True, using=database)
    try:
      # Logging the action
      log( category='CREATE', theuser=user,
        message = _('Start initializing dates')).save(using=database)

      # Delete the previous set of records
      connections[database].cursor().execute('DELETE FROM dates')
      transaction.commit(using=database)

      # Loop over all days in the chosen horizon
      while curdate < end:
        month = int(curdate.strftime("%m"))  # an integer in the range 1 - 12
        quarter = (month-1) / 3 + 1          # an integer in the range 1 - 4
        year = int(curdate.strftime("%Y"))
        dayofweek = int(curdate.strftime("%w")) # day of the week, 0 = sunday, 1 = monday, ...
        year_start = date(year,1,1)
        year_end = date(year+1,1,1)
        week_start = curdate - timedelta((dayofweek+6)%7)
        week_end = curdate - timedelta((dayofweek+6)%7-7)
        if week_start.date() < year_start: week_start = year_start
        if week_end.date() > year_end: week_end = year_end
        
        # Main entry
        Dates(
          day = str(curdate.date()),
          day_start = curdate,
          day_end = curdate + timedelta(1),
          dayofweek = dayofweek,
          week = curdate.strftime("%y W%W"),     # Weeks are starting on monday
          week_start = week_start,
          week_end = week_end,
          month =  curdate.strftime("%b %y"),
          month_start = date(year, month, 1),
          month_end = date(year+month/12, month+1-12*(month/12), 1),
          quarter = "%02d Q%s" % (year-2000,quarter),
          quarter_start = date(year, quarter*3-2, 1),
          quarter_end = date(year+quarter/4, quarter*3+1-12*(quarter/4), 1),
          year = curdate.strftime("%Y"),
          year_start = year_start,
          year_end = year_end,
          ).save(using=database)

        # Next date
        curdate = curdate + timedelta(1)

      # Log success
      log(category='CREATE', theuser=user,
        message=_('Finished initializing dates')).save(using=database)

    except Exception, e:
      # Log failure and rethrow exception
      try: log(category='CREATE', theuser=user,
        message=u'%s: %s' % (_('Failure initializing dates'),e)).save(using=database)
      except: pass
      if nonfatal: raise e
      else: raise CommandError(e)
      
    finally:
      # Commit it all, even in case of exceptions
      try: transaction.commit(using=database)
      except: pass
      settings.DEBUG = tmp_debug
      transaction.leave_transaction_management(using=database)
