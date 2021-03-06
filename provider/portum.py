from datetime import datetime, timedelta
from provider.utils import get_filtered_fb_post, on_workdays, skip_empty_lines


URL = "https://www.facebook.com/PortumCorvin/posts/"
FB_ID = "728866253985071"

@on_workdays
def getMenu(today):
    is_this_week = lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').date() > today.date() - timedelta(days=7)
    menu_filter = lambda post: is_this_week(post['created_time']) and \
        any(word in post['message'].lower() for word in ["lunch menü ", "business lunch", "előételek", "déli menü", "heti menü", "menünk"])
    menu = get_filtered_fb_post(FB_ID, menu_filter)
    drop_words = ["előételek", "főételek", "desszer", "étvágy", "menü", "lunch"]
    menu = skip_empty_lines(filter(lambda l: not any(word in l.lower() for word in drop_words), menu.splitlines()))
    remove_emoji = lambda text: ''.join(char for char in text if ord(char) < 500)
    menu = [remove_emoji(m) for m in menu]

    return menu

menu = {
    'name': 'Portum',
    'id': 'pt',
    'url': URL,
    'get': getMenu,
    'ttl': timedelta(hours=23),
    'cards': []
}
