from datetime import datetime, timedelta
from itertools import dropwhile, islice
from provider.utils import get_filtered_fb_post, days_lower, skip_empty_lines, on_workdays, pattern_slice


FB_PAGE = "https://www.facebook.com/pg/kubalabarca/posts/"
FB_ID = "2454065824618853"

@on_workdays
def getMenu(today):
    is_this_week = lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').date() > today.date() - timedelta(days=7)
    menu_filter = lambda post: is_this_week(post['created_time']) and sum(day in post['message'].lower() for day in days_lower) >= 2
    menu = get_filtered_fb_post(FB_ID, menu_filter)
    menu = pattern_slice(menu.splitlines(), [days_lower[today.weekday()]], days_lower + ["menü"], inclusive=False)
    return '<br>'.join(skip_empty_lines(menu))

menu = {
    'name': 'Kubala Barcelona',
    'id': 'kbarc',
    'url': FB_PAGE,
    'get': getMenu,
    'ttl': timedelta(hours=23),
    'cards': []
}