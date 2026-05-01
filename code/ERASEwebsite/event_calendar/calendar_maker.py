from calendar import HTMLCalendar
from datetime import datetime
from html import escape


class EventCalendar(HTMLCalendar):
    """Custom HTMLCalendar that displays events on specific dates"""
    
    def __init__(self, events=None):
        """
        Initialize calendar with optional events dictionary
        """
        super().__init__()
        self.events = events or {}
    
    def formatday(self, day, weekday):
        """
        Return HTML for a single day cell
        
        Args:
            day: Day of month (0 for days outside month)
            weekday: Weekday number (0-6)
            events_for_day: List of event objects for this day
        """
        if day == 0:
            return '<td class="other-month"></td>'
        
        today = datetime.now().date()
        current_date = datetime(self.year, self.month, day).date()
        is_today = current_date == today
        
        cell_class = 'today' if is_today else ''
        cell_html = f'<td class="{cell_class}">'
        
        # Day number
        day_class = 'day-number-highlight' if is_today else 'day-number'
        cell_html += f'<div class="{day_class}">{day}</div>'

        for event in self.events.get(current_date, []):
            time_str = event.time.strftime('%I:%M %p').lstrip('0')
            cell_html += (
                f'<div class="event-pill" '
                f'data-event-id="{event.pk}" '
                f'data-title="{escape(event.title)}" '
                f'data-time="{escape(time_str)}" '
                f'data-description="{escape(event.description)}" '
                f'data-has-rsvp="{str(event.hasRSVP).lower()}" '
                f'onclick="openEventDetailModal(this)">'
                f'<span class="event-time">{escape(time_str)}</span> '
                f'<span class="event-title">{escape(event.title)}</span>'
                f'</div>'
            )
        
        cell_html += '</td>'
        return cell_html
    
    def formatweek(self, theweek):
        """Return HTML for a week (row)"""
        s = ''.join(self.formatday(d, wd)
                    for (d, wd) in theweek)
        return f'<tr>{s}</tr>'
    
    def formatmonth(self, theyear, themonth, withyear=True):
        """Return formatted month calendar"""
        self.year = theyear
        self.month = themonth
        
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="calendar-table">')
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


def get_calendar_html(year, month, events=None):
    """
    Generate calendar HTML for a specific month
    
    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        events_dict: Dictionary of events with date strings as keys
                    Example: {'2026-03-12': [{'title': 'Meeting', 'priority': 'high'}]}
    
    Returns:
        HTML string for the calendar
    """
    calendar = EventCalendar(events=events)
    return calendar.formatmonth(year, month)