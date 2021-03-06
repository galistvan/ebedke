import traceback
from datetime import datetime as dt, timedelta
from concurrent.futures import ThreadPoolExecutor, Future
from time import sleep, perf_counter
import sys
import json
from random import randint

import redis
from flask import Flask, jsonify, render_template, request
from requests.exceptions import Timeout

from provider.utils import days_lower, normalize_menu
from provider import *
import config

places = {
    "corvin": [tenminutes, tacsko, cbacorvin, dagoba, dezso, emi,
               foodie, gilice, golvonal, greenhouse, input, intenzo,
               joasszony, kerova, kompot, manga, muzikum, opus,
               portum, pqs, seastars, stex, veranda, zappa],

    "ferenciek": [fruccola, homefield, kajahu],

    "moricz": [keg, semmiextra, szatyor],

    "szepvolgyi": [officebistro, semmiextra, wasabi],

    "szell": [bocelli, ezisbudai, jegkert, joasszony, kbarcelona, pastafresca, vanbisztro],

    "default": [tenminutes, tacsko, bocelli, cbacorvin, dagoba, dezso, emi, ezisbudai, foodie, fruccola, gilice, golvonal,
                greenhouse, homefield, input, intenzo, jegkert, joasszony, kajahu, keg, kerova, kompot, kbarcelona, manga, muzikum,
                officebistro, opus, pastafresca, portum, pqs, semmiextra, seastars, stex, szatyor, vanbisztro, veranda,
                wasabi, zappa]
}

app = Flask(__name__, static_url_path='')
app.config.update(
    JSON_AS_ASCII=False
)

cache = redis.StrictRedis(host=config.REDIS_HOST,
                          port=config.REDIS_PORT)

def menu_loader(menu, today):
    start = perf_counter()
    daily_menu = None
    while daily_menu is None:
        if cache.set(f"{menu['id']}:lock", 1, ex=20, nx=True):
            try:
                daily_menu = menu['get'](today)
                assert isinstance(daily_menu, list)
            except Timeout:
                print(f"[ebedke] timeout in «{menu['name']}» provider")
                daily_menu = []
            except:
                print(f"[ebedke] exception in «{menu['name']}» provider:\n", traceback.format_exc())
                daily_menu = []
            daily_menu = normalize_menu(daily_menu)
            if daily_menu is not "":
                seconds_to_midnight = (23 - today.hour) * 3600 + (60 - today.minute) * 60
                ttl = min(int(menu['ttl'].total_seconds()), seconds_to_midnight)
            else:
                if today.hour >= 10 and today.hour <= 12:
                    ttl = randint(520, 540)
                elif today.hour < 10:
                    ttl = randint(1900, 2100)
                else:
                    ttl = randint(3000, 3200)
            if config.DEBUG_CACHE_HTTP:
                ttl = 10
            cache.set(menu['id'], json.dumps(daily_menu), ex=ttl)
        else:
            sleep(0.05)
            daily_menu = json.loads(cache.get(menu['id']))
    elapsed = perf_counter() - start
    print(f"[ebedke] loading «{menu['name']}» took {elapsed} seconds")
    return daily_menu


def load_menus(today, restaurants):
    if config.OFFSET:
        today = today + timedelta(days=config.OFFSET)

    with ThreadPoolExecutor(max_workers=config.POOL_SIZE) as executor:
        menus = [(provider,
                  executor.submit(menu_loader, provider.menu, today) if menu is None else menu)
                 for provider, menu in
                 zip(restaurants,
                     cache.mget(provider.menu['id'] for provider in restaurants))
                ]
    out = [{"name": provider.menu['name'],
             "url": provider.menu['url'],
             "id": provider.menu["id"],
             "menu": menu.result() if isinstance(menu, Future) else menu,
             "cards": provider.menu.get('cards', [])
            } for provider, menu in menus]

    return out

@app.route('/')
def root():
    subdomain = request.host.split(".ebed.today")[0]
    if subdomain in places:
        restaurants = places[subdomain]
        welcome = False
    else:
        restaurants = places['default']
        welcome = True

    today = dt.today()
    date = {
        'day': days_lower[today.weekday()],
        'date': today.strftime("%Y. %m. %d.")
    }
    return render_template("index.html", menus=load_menus(today, restaurants), date=date, welcome=welcome)

@app.route('/menu')
def dailymenu():
    subdomain = request.host.split(".ebed.today")[0]
    if subdomain in places:
        restaurants = places[subdomain]
    else:
        restaurants = places['default']

    jsonout = [{"name": menu['name'],
             "url": menu['url'],
             "menu": '<br>'.join(menu['menu']),
             "cards": menu['cards']
            } for menu in load_menus(dt.today(), restaurants)]

    return jsonify(jsonout)

@app.route('/menu.json')
def api_v1():
    subdomain = request.host.split(".ebed.today")[0]
    if subdomain in places:
        restaurants = places[subdomain]
    else:
        restaurants = places['default']

    jsonout = [{"name": menu['name'],
             "url": menu['url'],
             "menu": list(menu['menu']),
             "cards": menu['cards']
            } for menu in load_menus(dt.today(), restaurants)]

    return jsonify(jsonout)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        provider = sys.argv[1]
        offset_base = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        items = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        for i in range(items):
            print(globals()[provider].menu['get'](dt.today() + timedelta(days=offset_base + i)))
    else:
        app.run(debug=True, use_reloader=True, host='0.0.0.0')
