# -*- coding: utf-8 -*-

import requests
import io
import icalendar
import datetime
import traceback
from urllib.parse import urlparse

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pytz import reference

from nikola.plugin_categories import RestExtension
from nikola.utils import req_missing
import nikola


def get_ics_content(url):
  if urlparse(url).scheme == 'file':
    with open(url) as f:
      ics = f.read()
  else:
    r = requests.get(url)
    ics = r.text

  cal = icalendar.Calendar.from_ical(ics)

  return map(lambda c: {
    'summary': c.get('summary'),
    'location': c.get('location'),
    'description': c.get('description'),
    'start': c.get('dtstart').dt,
    'end': c.get('dtend').dt,
  }, cal.walk('VEVENT'))

def group_events(events):
  today = datetime.datetime.now(tz=reference.LocalTimezone())

  past_events = []
  upcoming_events = []

  for event in events:
    if event['start'] < today:
      upcoming_events.append(event)
    else:
      past_events.append(event)

  past_events.sort(key=lambda e: e['start'])
  upcoming_events.sort(key=lambda e: e['start'])

  return past_events, upcoming_events

def generate_rst_title(title, type='-'):
  return '\n{0}\n{1}'.format(title, type * len(title))

def generate_rst_eventlist(events):
  last_month = None

  for event in events:
    cur_month = event['start'].month
    if last_month != cur_month:
      yield generate_rst_title(event['start'].strftime('%B %Y'), '-')

    last_month = event['start'].month
    yield '* {start}, {summary}'.format(**event)

def ics2rest(url):
  events = group_events(get_ics_content(url))

  s = ''

  s += generate_rst_title('kommende Events', '=')
  s += "\n".join(generate_rst_eventlist(events[0]))
  s += "\n\n"

  s += generate_rst_title('vergangene Events', '=')
  s += "\n".join(generate_rst_eventlist(events[1]))
  s += "\n\n"

  return s


class Plugin(RestExtension):
    """Plugin for reST ."""

    name = "rest_ics"

    def _gen_ics_rst(self, site, data):
        comp = nikola.plugins.compile.rest.CompileRest()
        comp.set_site(site)
        try:
          return comp.compile_html_string(ics2rest(data))[0]
        except:
          traceback.print_exc()
          return '<i>Die Events konnten leider nicht geladen werden. Bitte später erneut versuchen.</i>'

    def set_site(self, site):
        self.site = site
        self.site.register_shortcode('ics', self._gen_ics_rst)
        return super(Plugin, self).set_site(site)
