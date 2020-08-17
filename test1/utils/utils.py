import extruct
import pprint

pp = pprint.PrettyPrinter(indent=2)

metadata_type_map = {
    'next_book_link': ['http://schema.org/Book'],
    'book': ['http://schema.org/Book'],
}

wanted_property_map = {
    'next_book_link': {
        'url': ["properties", "url"]
    },
    'book': {
        'rating': ['properties', 'aggregateRating', 'properties', 'ratingValue'],
        'title': ['properties', 'name'],
    }
}

syntaxes = ['microdata']


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


def get_nested_value_from_dict(dct, keys, default = ''):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct
