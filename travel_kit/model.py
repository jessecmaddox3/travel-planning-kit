"""Small explicit data rules shared by every renderer and the local editor."""
from datetime import date
from decimal import Decimal
import re
from urllib.parse import urlsplit


class ValidationError(ValueError):
    """An editable field needs correction; the last good document is unchanged."""


CURRENCY_DIGITS = {'USD': 2, 'EUR': 2, 'GBP': 2, 'CAD': 2, 'AUD': 2, 'JPY': 0, 'KWD': 3}
TRIP_TAGS = {'universal', 'beach', 'camping', 'road-trip'}


def currency_digits(currency):
    if not isinstance(currency, str) or currency not in CURRENCY_DIGITS:
        raise ValidationError('Choose a supported currency: ' + ', '.join(CURRENCY_DIGITS))
    return CURRENCY_DIGITS[currency]


def amount(value, currency):
    digits = currency_digits(currency)
    pattern = r'\d{1,9}' + (rf'(?:\.\d{{1,{digits}}})?' if digits else '')
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValidationError(f'Use a nonnegative {currency} amount as a decimal string, without commas or currency symbols.')
    return Decimal(value)


def quote_value(quote):
    """Validate numeric structure without inventing an exact price for an estimate."""
    if not isinstance(quote, dict):
        raise ValidationError('A price quote must be an object.')
    currency = quote.get('currency', 'USD')
    currency_digits(currency)
    kind = quote.get('kind')
    if kind == 'exact':
        return amount(quote.get('amount'), currency)
    if kind == 'range':
        lower, upper = amount(quote.get('min'), currency), amount(quote.get('max'), currency)
        if lower > upper:
            raise ValidationError('The low end of a price range must not exceed its high end.')
        return None
    if kind == 'unknown':
        return None
    raise ValidationError('A quote kind must be exact, range or unknown.')


def split_quote(quote, count):
    """Allocate all minor units exactly; extra households pay one unit more."""
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValidationError('A split needs a whole household count from 1 to 10000.')
    total = quote_value(quote)
    if total is None:
        return None
    currency = quote.get('currency', 'USD')
    digits = currency_digits(currency)
    scale = 10 ** digits
    base, extra = divmod(int(total * scale), count)
    return {'currency': currency, 'amount': f'{Decimal(base) / scale:.{digits}f}',
            'extra_amount': f'{Decimal(base + bool(extra)) / scale:.{digits}f}',
            'extra_count': extra, 'count': count}


def safe_url(value):
    """External links are explicit HTTP(S) links, never executable/local schemes."""
    if not isinstance(value, str) or len(value) > 4096:
        raise ValidationError('A link must be text shorter than 4097 characters.')
    if not value:
        return ''
    if any(ord(c) < 33 or ord(c) == 127 for c in value) or '\\' in value:
        raise ValidationError('Links cannot contain spaces, control characters or backslashes.')
    try:
        url = urlsplit(value)
        valid = url.scheme in {'http', 'https'} and url.hostname and url.username is None and url.password is None
        _ = url.port
    except ValueError:
        valid = False
    if not valid:
        raise ValidationError('Use an http:// or https:// link without a username or password.')
    return value


def iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValidationError('Use a date in YYYY-MM-DD form.')
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValidationError('That calendar date does not exist.') from error


def validate_dates(start, end):
    nights = (iso_date(end) - iso_date(start)).days
    if not 1 <= nights <= 3660:
        raise ValidationError('Departure must follow arrival by 1 to 3660 nights.')
    return nights


def select_items(items, packing):
    """Tag suggestions plus manual inclusions, with exclusions taking precedence."""
    ids = [item['id'] for item in items]
    if len(ids) != len(set(ids)):
        raise ValidationError('Catalog item IDs must be unique.')
    known = set(ids)
    for field in ('selected', 'excluded', 'morning'):
        values = packing.get(field, [])
        if not isinstance(values, list) or any(not isinstance(x, str) or x not in known for x in values):
            raise ValidationError(f'Packing {field} references an unknown catalog item.')
    tags = set(packing.get('tags', []))
    if not tags <= TRIP_TAGS:
        raise ValidationError('Choose universal, beach, camping or road-trip tags.')
    included, excluded = set(packing.get('selected', [])), set(packing.get('excluded', []))
    return [item for item in items if item['id'] not in excluded and
            (item['id'] in included or 'universal' in item.get('tags', []) or tags.intersection(item.get('tags', [])))]
