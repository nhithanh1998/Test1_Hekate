import extruct
import pprint

pp = pprint.PrettyPrinter(indent=2)

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
        'rating': ['properties', 'aggregateRating', 'properties', 'ratingValue'],
        'title': ['properties', 'name'],
        'author': ['properties', 'author', 'properties', 'name'],
        'reviews': ['properties', 'reviews']
    },
    'review': {
        'review_url': ['properties', 'reviews', 'properties', 'author'],
        'review_content': ['properties', 'reviews', 'properties', 'reviewBody'],
        'rate': ['properties', 'reviews', 'properties', 'reviewRating', 'properties', 'ratingValue'],
        'date_published': ['properties', 'reviews', 'properties', 'datePublished']
    }
}

syntaxes = ['microdata']


def extract_data(raw, url, wanted_value, flag = 1):
    data = extruct.extract(raw, base_url=url, syntaxes=syntaxes)
    if wanted_value == 'review':
        flag = 0
    rs = extract_data_from_microdata(data['microdata'], metadata_type_map[wanted_value],
                                     wanted_property_map[wanted_value], flag)

    return rs


def extract_data_from_microdata(microdata, schema_type, wanted_properties={}, flag=1):
    rs = []
    items = [item for item in microdata if item['type'] in schema_type]
    for item in items:
        rs.append({key: get_nested_value_from_dict(item, wanted_properties[key]) for key in wanted_properties.keys()})
    return rs


def get_nested_value_from_dict(dct, keys, default=''):
    if type(dct) is dict:
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return default
        return dct
    elif type(dct) is list:
        return [get_nested_value_from_dict(dct=item, keys=keys, default=default) for item in dct]


