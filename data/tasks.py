import time

import requests
from celery import shared_task
from celery.utils.log import get_task_logger

from .config import paxful_conf
from .models import (Category, CurrencyDetail, Offer, OfferDetail, Subcategory,
                     Tag)
from .utils import generate_url, merge_lang, str2bool, str_to_dict

logger = get_task_logger(__name__)


DOMAIN = paxful_conf['domain']
HEADERS = paxful_conf['headers']


def update_offer(offer, data):
    # Update warranty data if exist
    if 'Warranty period (usage time):' in data:
        warranty_start = data.index('Warranty period (usage time)')
        warranty_end = data[warranty_start::].index('\n')
        warranty = data[warranty_start:warranty_start+warranty_end].split(':')[1].strip()
        if warranty[0].isdigit():
            offer.warranty = warranty

    # Update readme link if exist
    if 'Read more (FAQ):' in data:
        faq_start = data.index('Read more (FAQ)')
        faq_end = data[faq_start::].index('\n')
        faq = data[faq_start:faq_start+faq_end].split(':')
        faq = ':'.join(faq[1::]).strip()
        if 'paxful' not in faq:
            subcategory = Subcategory.objects.get(id=offer.subcategory.id)
            if not subcategory.faq:
                subcategory.faq = faq
                subcategory.save()
    offer.description = data
    return offer


@shared_task
def updateOfferDescription(offers=None):
    print('UPDATING offer description')
    if not offers:
        offers = Offer.objects.all()
    x = 0
    while x != len(offers)-1:
        res = requests.get(
            f'https://paxful.com/offer/{offers[x].px_id}', headers=HEADERS, verify=False
        )
        #print(f'[{x+1}] Updating Data for {offers[x].px_id, offers[x].username}\n{offers[x].__str__()}\nStatus Code: {res.status_code}')
        if res.status_code == 200:
            start = res.text.index('offerTerms')
            end = res.text.index('noCoins"')
            desc = str_to_dict('{"' + res.text[start:end][:-2]+'}')
            if desc['offerTerms'] != '':
                try:
                    offer = update_offer(offers[x], desc['offerTerms'])
                    offer.save()
                except Exception as _ex:
                    print(_ex)
            else:
                offers[x].description = None
                offers[x].save()
            time.sleep(1)
            x += 1
        elif res.status_code in [404, 410]:
            print(f'DELETE: {offers[x].px_id, offers[x].username}\nPage not Found')
            offers[x].delete()
            x += 1
        else:
            time.sleep(15)
    print('UPDATING offer description END')


@shared_task
def updatePaxfullOffers():
    print('UPDATING Paxful Offers')
    sell_conf = paxful_conf['sell']
    cur = paxful_conf['crypto_currency_id']
    data = list()
    offer_desc = list()
    for code, id in cur.items():
        sell_conf['params']['crypto_currency_id'] = id
        URL = generate_url(
            [DOMAIN, sell_conf['url']['dir']], sell_conf['params']
        )
        res = requests.get(URL, headers=HEADERS, verify=False)
        if res.status_code == 200:
            data = str_to_dict(res.text)['data']
            print(f'TOTAL: {len(data)} {code}')
            default_category = Category.objects.get(name='Other')
            offers = list()
            
            for offer in data:
                if offer['pricePerUsd'] >= 1.1:
                    offers.append(offer['idHashed'])
                    
                    tags = list()
                    if offer['tags']:
                        ids = [tag['id'] for tag in offer['tags']]
                        tags = Tag.objects.filter(px_id__in=ids)
                    sub_cat_values = {
                        'px_id': 0,
                        'ru_name': offer['paymentMethodName'],
                        'category': default_category
                    }
                    sub_cat, created = Subcategory.objects.get_or_create(
                        name=offer['paymentMethodName'],
                        defaults=sub_cat_values
                    )
                    if created:
                        print(f'Object of {sub_cat} was created')

                    offer_detail_values = {
                        'feedback_negative': offer['feedbackNegative'],
                        'feedback_positive': offer['feedbackPositive'],
                        'predefined_amount': offer['predefinedAmount'],
                        'fiat_amount_range_min': offer['fiatAmountRangeMin'],
                        'fiat_amount_range_max': offer['fiatAmountRangeMax'],
                        'fiat_price_per_btc': offer['fiatPricePerBtc'],
                        'price_per_btc': offer['pricePerBtc'],
                        'fee_percentage': offer['feePercentage'],
                        'payment_method_group_id': offer['paymentMethodGroupId'],
                        'percent_per_usd': offer['percentPerUsd'],
                        'require_full_name_visibility': str2bool(offer['requireFullNameVisibility']),
                        'default_flow_type': offer['defaultFlowType'],
                    }
                    offer_detail, created = OfferDetail.objects.update_or_create(
                        px_id=offer['idHashed'], defaults=offer_detail_values
                    )
                        
                    offer_values = {
                        'sell_cur': offer['cryptoCurrencyCode'],
                        'buy_cur': offer['fiatCurrencyCode'],
                        'currency': CurrencyDetail.objects.filter(code=offer['fiatCurrencyCode']).first(),
                        'margin': offer['margin'],
                        'price_per_cur': offer['pricePerUsd'],
                        'require_verified_id': str2bool(offer['requireVerifiedId']),
                        'category': sub_cat.category,
                        'subcategory': sub_cat,
                        'payment_method_label': offer['paymentMethodLabel'],
                        'username': offer['username'],
                        'score': offer['score'],
                        'last_seen': offer['lastSeenString'],
                        'average_trade_speed': offer['releaseTimeMedianHumanize'],
                        'user_timezone': offer['userTimezone'],
                        'offer_type': offer['offerType'],
                        'offer_detail': offer_detail,
                        'is_active': True
                    }
                    offer, created = Offer.objects.update_or_create(
                        px_id=offer['idHashed'], defaults=offer_values
                    )
                    offer.tags.set(tags)
                    if created:
                        offer_desc.append(offer)
                        print(f'CREATED {offer}')
                        
            outdated_offers = Offer.objects.filter(sell_cur=code, is_active=True).exclude(px_id__in=offers)
            print(f'RECEIVED: {len(offers)} | REMOVED: {len(outdated_offers)} | CREATED: {len(offer_desc)} offers.')
            offers = Offer.objects.all()
            print(f'ACTIVE: {len(offers.filter(is_active=True))} | INACTIVE: {len(offers.filter(is_active=False))}')
            outdated_offers.update(is_active=False)
            print('UPDATING Paxful Offers END')
            if offer_desc:
                updateOfferDescription(offer_desc)

        else:
            print(f'Error {res.status_code}: Data was not found for {code}.')
            return res.status_code


@shared_task(name='updateTags')
def updateTags():
    tag_conf = paxful_conf['tags']
    URL = generate_url([DOMAIN, tag_conf['url']['dir']])
    res = requests.get(URL, headers=HEADERS)
    logger.info('HEEEREE')
    if res.status_code == 200:
        data = str_to_dict(res.text)['data']
        for tag in data:
            values = {
                'name': tag['name'],
                'description': tag['description'],
                'px_slug': tag['slug'],
            }
            obj, created = Tag.objects.update_or_create(
                px_id=tag['id'], defaults=values
            )
            if created:
                print(f'Created new obj of {obj}')
            else:
                print(f'Updated new obj of {obj}')
    else:
        return 400, f'Error {res.status_code}: Data was not found by {URL}'


def updateCategories():
    cat_conf = paxful_conf['categories']
    EN_CAT_URL = generate_url(
        [DOMAIN, cat_conf['url']['lang']['en'], cat_conf['url']['dir']]
    )
    RU_CAT_URL = generate_url(
        [DOMAIN, cat_conf['url']['lang']['ru'], cat_conf['url']['dir']]
    )
    res = requests.get(EN_CAT_URL, headers=HEADERS)
    if res.status_code == 200:
        en_data = str_to_dict(res.text)['data']
        res = requests.get(RU_CAT_URL, headers=HEADERS)
        if res.status_code == 200:
            ru_data = str_to_dict(res.text)['data']
            data = merge_lang(en=en_data, ru=ru_data, field='name')
            for category in data:
                values = {
                    'name': category['category_name'],
                    'ru_name': category['ru_name'],
                    'px_slug': category['slug']
                }
                obj, created = Category.objects.update_or_create(
                    px_id=category['id'], defaults=values
                )
                if created:
                    print(f'Created new obj of {obj}')
                else:
                    print(f'Updated new obj of {obj}')
        else:
            return 400, f'Error {res.status_code}: Data was not found by {RU_CAT_URL}'
    else:
        return 400, f'Error {res.status_code}: Data was not found by {EN_CAT_URL}'
    
    
@shared_task
def updateSubCategories():
    s_cat_conf = paxful_conf['subcategory']
    EN_S_CAT_URL = generate_url(
        [DOMAIN, s_cat_conf['url']['lang']['en'], s_cat_conf['url']['dir']],
        s_cat_conf['params']
    )
    RU_S_CAT_URL = generate_url(
        [DOMAIN, s_cat_conf['url']['lang']['ru'], s_cat_conf['url']['dir']],
        s_cat_conf['params']
    )
    res = requests.get(EN_S_CAT_URL, headers=HEADERS)
    if res.status_code == 200:
        en_data = str_to_dict(res.text)['data']
        res = requests.get(RU_S_CAT_URL, headers=HEADERS)
        if res.status_code == 200:
            ru_data = str_to_dict(res.text)['data']
            data = merge_lang(en=en_data, ru=ru_data, field='name')
            updateCategories()
            for s_cat in data:
                category = Category.objects.filter(px_id=s_cat['gift_card_category_id']).first()
                if category:
                    values = {
                        'name': s_cat['name'],
                        'ru_name': s_cat['ru_name'],
                        'px_slug': s_cat['slug'],
                        'category': category
                    }
                    obj, created = Subcategory.objects.update_or_create(
                        px_id=s_cat['id'], defaults=values
                    )
                    if created:
                        print(f'Created new obj of {obj}')
                    else:
                        print(f'Updated new obj of {obj}')
                else:
                    print(f'Fatal Error {res.status_code}: Category not found for {s_cat}')
        else:
            return 400, f'Error {res.status_code}: Data was not found by {RU_S_CAT_URL}'
    else:
        return 400, f'Error {res.status_code}: Data was not found by {EN_S_CAT_URL}'
    