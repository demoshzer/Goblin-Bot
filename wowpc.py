#!/usr/bin/env python3.5

import os
import sys
import requests
import asyncio
import discord


# Load realm data
r = requests.get('https://theunderminejournal.com/api/realms.php')
realm_data = r.json()

us_realms = {
    realm['name']: {
        'locale': realm['locale'],
        'house': realm['house']
    } for realm in realm_data['realms'][0].values()
}

eu_realms = {
    realm['name']: {
        'locale': realm['locale'],
        'house': realm['house']
    } for realm in realm_data['realms'][1].values()
}

def match_realm(region, name):
    if region == 'us':
        realms = us_realms
    else:
        realms = eu_realms
    return next( (realm for realm in realms if realm.startswith(name.capitalize())), None)


def tuj_search(region, realm, item):
    if region not in ['us', 'eu']:
        raise Exception('Invalid region. Must be "us" or "eu"')
    realm = match_realm(region, realm)
    if realm is None:
        raise Exception('Realm not found, did you spell it correctly?')
    if region == 'us':
        locale = us_realms[realm]['locale']
        house = us_realms[realm]['house']
    else:
        locale = eu_realms[realm]['locale']
        house = eu_realms[realm]['house']
    params = {
        'locale': locale,
        'house': house,
        'search': item
    }
    r = requests.get('https://theunderminejournal.com/api/search.php', params=params)
    items = r.json()['items']
    if items is None:
        raise Exception('Item not found, did you spell it correctly?')
    stats = items[0]
    stats['realm'] = realm
    stats['price'] = "%.2fg" % (stats['price']/10000)
    stats['avgprice'] = "%.2fg" % (stats['avgprice']/10000)
    stats['url'] = 'https://theunderminejournal.com/#{0}/{1}/item/{2}'.format(region, realm.lower(), stats['id'])
    return stats


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')

@client.event
async def on_message(message):
    if message.content.startswith('!pc'):
        args = message.content.split()
        if len(args) < 4:
            return
        region, realm, item = args[1:4]
        try: 
            stats = tuj_search(region, realm, item)
        except Exception as e:
            await client.send_message(message.channel, str(e))
            return
        stat_msg = '{0} {1} - Price: {2}, Average Price: {3}, Quantity: {4} {5}'.format(
            stats['realm'], stats['name_enus'], stats['price'], stats['avgprice'], 
            stats['quantity'], stats['url'])
        await client.send_message(message.channel, stat_msg)


client.run(os.environ['WOWPCTOKEN'])

