# -*- coding: utf-8 -*-
import re

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import random
import string

from djeym.models import CustomMarkerIcon, LoadIndicator, Map, TileSource
import logging


logger = logging.getLogger('custom_app')

register = template.Library()


@register.inclusion_tag('djeym/includes/loadymap.html', takes_context=True)
def djeym_load_ymap(context, slug='', panel='djeym/includes/panel.html',
                    header='djeym/includes/map_header.html', load_api=True, global_buttons=False):
    """Load YMap"""
    ymap = Map.objects.filter(slug=slug, active=True).first()
    logger.debug("Map: {}".format(ymap))
    result = {'ymap': ymap,
              'load_api': load_api,
              'global_buttons': global_buttons}

    if ymap is not None:
        result.update({
            'language_code': context['request'].LANGUAGE_CODE,
            'cluster': ymap.icon_cluster,
            'tile': ymap.tile,
            'presets': ymap.presets.all(),
            'controls': ymap.controls,
            'external_modules': ymap.external_modules,
            'heatmap_settings': ymap.heatmap_settings,
            'general_settings': ymap.general_settings,
            'load_indicators': LoadIndicator.objects.all(),
            'selected_load_indicator': ymap.load_indicator,
            'load_indicator_size': ymap.load_indicator_size
        })

        if not ymap.general_settings.disable_site_panel or not ymap.general_settings.disable_map_header:
            result.update({
                'category_placemarks': ymap.category_placemark.filter(active=True),
                'category_submarks': ymap.subcategory_placemark.filter(active=True),
                'category_polylines': ymap.category_polyline.filter(active=True),
                'category_polygons': ymap.category_polygon.filter(active=True),
            })

        if not ymap.general_settings.disable_site_panel:
            result.update({
                'panel_path': panel
            })

        if not ymap.general_settings.disable_map_header:
            result.update({
                'header_path': header
            })

    return result


@register.inclusion_tag('djeym/includes/api_and_plugins.html', takes_context=True)
def get_api_ymap(context, lang="", ns='djeymYMaps'):
    """Get API for Yandex map"""

    api_version = '2.1'
    api_key = getattr(settings, 'DJEYM_YMAPS_API_KEY', "")
    mode = getattr(settings, 'DJEYM_YMAPS_DOWNLOAD_MODE', 'release')
    lang = lang[:2].lower() if len(lang) > 0 else \
        getattr(settings, 'LANGUAGE_CODE', "en")[:2].lower()

    if lang == 'ru':
        lang += '_RU'
    elif lang == 'en':
        lang += '_US'
    elif lang == 'uk':
        lang += '_UA'
    elif lang == 'tr':
        lang += '_TR'
    else:
        lang = 'en_US'

    return {
        'api_key': api_key,
        'api_version': api_version,
        'lang': lang,
        'mode': mode,
        'ns': ns,
        'external_modules': context.get('external_modules'),
        'presets': context.get('presets'),
    }


@register.simple_tag
def random_domain(value, apikey=""):
    """Tile Sources - Add random selection of subdomains, api key"""
    count_elem = re.search(r'\[\[(.+)\]\]', value)

    if count_elem is not None:
        count_elem = len(eval(count_elem.group(0))[0])

    value = re.sub(r'\[(\[.+\])\]',
                   '" + \\1[ Math.round( Math.random() * {} ) ] + "'
                   .format(int(count_elem) - 1), value)
    if len(apikey) > 0:
        var_key = re.search(r'\{\{(.+)\}\}', value).group(0)
        clean_var_key = re.sub(r'{{|}}', "", var_key)
        value = value.replace(var_key, clean_var_key + apikey, 1)
    else:
        value = re.sub(r'\{\{.+\}\}', "", value)
    return mark_safe(value)


@register.inclusion_tag('djeym/includes/geocoder.html', takes_context=True)
def ymap_geocoder(context, address="", controls="zoom", tile_slug='default',
                  marker_slug='default', load_indicator_slug='default', size='64', speed='0.8', load_api=True):

    load_indicator = LoadIndicator.objects.filter(
        slug=load_indicator_slug).first()

    result = {
        'language_code': context['request'].LANGUAGE_CODE,
        'address': address,
        'controls': True if controls != 'all' else False,
        'tile': TileSource.objects.filter(slug=tile_slug).first(),
        'marker': CustomMarkerIcon.objects.filter(slug=marker_slug).first(),
        'load_indicator': load_indicator.svg.url if
        load_indicator is not None else '/static/djeym/img/spinner.svg',
        'load_indicator_size': size,
        'speed': speed,
        'load_api': load_api
    }

    return result


@register.inclusion_tag('djeym/includes/distance.html')
def distance(point1, point2):
    result = {
        'point1': point1,
        'point2': point2,
        'unique_id': ''.join([random.choice(string.ascii_lowercase) for i in range(8)])
    }
    return result


@register.inclusion_tag('djeym/includes/coordinates_saver.html', takes_context=True)
def coordinates_saver(context):
    return {}
