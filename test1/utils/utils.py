import extruct
import re


# below is the two object for easily declare what value need and how to get it

metadata_type_map = {
    'next_book_link': ['http://schema.org/Book'],
    'book': ['http://schema.org/Book'],
    'review': ['http://schema.org/Book']
}

wanted_property_map = {
    'next_book_link': {
        'url': ["properties", "url"]
    },
    'book': {
        'rate': ['properties', 'aggregateRating', 'properties', 'ratingValue'],
        'title': ['properties', 'name'],
        'author': ['properties', 'author', 'properties', 'name'],
        'reviews': ['properties', 'reviews']
    },
    'review': {
        'reviewer_url': ['properties', 'reviews', 'properties', 'author'],
        'content': ['properties', 'reviews', 'properties', 'reviewBody'],
        'rate': ['properties', 'reviews', 'properties', 'reviewRating', 'properties', 'ratingValue'],
        'date_posted': ['properties', 'reviews', 'properties', 'datePublished']
    }
}

# meta_data full syntax = ['microdata', 'json-ld', 'microformat', 'opengraph', 'rdfa']
# but only with microdata we can get all we need from good_read side

syntaxes = ['microdata']


# extract_data currently enable only microdata but in future new may come in town, so I return array here so we don't
# need to adjust so many in the future

def extract_data(raw, url, wanted_value):
    data = extruct.extract(raw, base_url=url, syntaxes=syntaxes)
    rs = extract_data_from_microdata(data['microdata'], metadata_type_map[wanted_value],
                                     wanted_property_map[wanted_value])
    return rs


def extract_data_from_microdata(microdata, schema_type, wanted_properties={}):
    rs = []
    items = [item for item in microdata if item['type'] in schema_type]
    for item in items:
        rs.append({key: get_nested_value_from_dict(item, wanted_properties[key]) for key in wanted_properties.keys()})
    return rs


# safe get value from nested key if the chain occurred any error it will return default value

def get_nested_value_from_dict(dct, keys, default=''):
    if type(dct) is dict:
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return default
        return dct
    elif type(dct) is list:
        # not safe yet may encounter error if error occur
        return [get_nested_value_from_dict(dct=item, keys=keys, default=default) for item in dct]


def get_id_from_link(url):
    pattern = r"(?!.*\/).*?(?=-)"
    return re.findall(pattern, url)[0]