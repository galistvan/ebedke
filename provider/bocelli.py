from datetime import datetime, timedelta
from provider.utils import get_filtered_fb_post, skip_empty_lines, on_workdays


FB_PAGE = "https://www.facebook.com/pg/bocellipizzeria/posts/"
FB_ID = "401839609844340"

@on_workdays
def getMenu(today):
    is_today = lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').date() == today.date()
    menu_keywords = ["chef", "ajánlat", "1490", "1390", ",-", ".-", "ára"]

    menu_filter = lambda post: is_today(post['created_time']) and any(word in post['message'].lower() for word in menu_keywords)

    menu = get_filtered_fb_post(FB_ID, menu_filter)
    menu = (line for line in menu.splitlines() if not any(word in line.lower() for word in menu_keywords))

    return list(skip_empty_lines(menu))

menu = {
    'name': 'Bocelli Pizzeria Italia',
    'id': 'boc',
    'url': FB_PAGE,
    'get': getMenu,
    'ttl': timedelta(hours=23),
    'cards': []
}
