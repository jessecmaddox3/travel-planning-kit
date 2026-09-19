import unittest
from decimal import Decimal
from travel_kit.model import quote_value, split_quote, safe_url, select_items, validate_dates, ValidationError

class MoneyTests(unittest.TestCase):
    def test_exact_cents_and_remainder_are_preserved(self):
        quote={'kind':'exact','currency':'USD','amount':'1234.57'}
        self.assertEqual(quote_value(quote), Decimal('1234.57'))
        split=split_quote(quote,3)
        self.assertEqual(split, {'currency':'USD','amount':'411.52','extra_amount':'411.53','extra_count':1,'count':3})
    def test_ranges_and_unknowns_have_no_exact_split(self):
        for quote in [{'kind':'range','currency':'USD','min':'900.00','max':'1200.00'}, {'kind':'unknown','currency':'USD','note':'Ask for a quote'}]:
            self.assertIsNone(quote_value(quote));self.assertIsNone(split_quote(quote,2))
    def test_no_false_numeric_prices_or_invalid_splits(self):
        for value in ['NaN','Infinity','1e4','-5','1,200.00','1.234','100000000000000000']:
            with self.subTest(value=value),self.assertRaises(ValidationError):quote_value({'kind':'exact','currency':'USD','amount':value})
        for count in [0,-1,True,1.5,10001]:
            with self.subTest(count=count),self.assertRaises(ValidationError):split_quote({'kind':'exact','currency':'USD','amount':'10.00'},count)
    def test_currency_precision_is_explicit(self):
        self.assertEqual(split_quote({'kind':'exact','currency':'JPY','amount':'1001'},2)['extra_amount'],'501')
        self.assertEqual(split_quote({'kind':'exact','currency':'KWD','amount':'1.001'},2)['extra_amount'],'0.501')
        with self.assertRaises(ValidationError):quote_value({'kind':'exact','currency':'XYZ','amount':'1.00'})
        with self.assertRaises(ValidationError):quote_value({'kind':'range','currency':'USD','min':'10.00','max':'2.00'})

class InputTests(unittest.TestCase):
    def test_links_cannot_execute_or_include_credentials(self):
        for url in ['javascript:alert(1)','file:///private/item','https://user:secret@example.invalid/x','https://example.invalid/\nheader','//example.invalid']:
            with self.subTest(url=url),self.assertRaises(ValidationError):safe_url(url)
        self.assertEqual(safe_url('https://example.invalid/listing?a=1&b=2'),'https://example.invalid/listing?a=1&b=2')
        self.assertEqual(safe_url(''),'')
    def test_manual_selection_survives_tag_suggestions(self):
        items=[{'id':'coat','tags':['universal']},{'id':'tent','tags':['camping']},{'id':'mask','tags':['beach']}]
        packing={'tags':['beach'],'selected':['tent'],'excluded':['mask'],'morning':['coat']}
        self.assertEqual([x['id'] for x in select_items(items,packing)],['coat','tent'])
        self.assertEqual(packing['selected'],['tent'])
        with self.assertRaises(ValidationError):select_items(items,{**packing,'selected':['missing']})
    def test_real_dates_and_stay_order(self):
        self.assertEqual(validate_dates('2034-09-07','2034-09-10'),3)
        for a,b in [('2034-02-30','2034-03-01'),('2034-09-10','2034-09-07'),('2034-09-07','2034-09-07')]:
            with self.subTest(a=a,b=b),self.assertRaises(ValidationError):validate_dates(a,b)

if __name__=='__main__':unittest.main()
