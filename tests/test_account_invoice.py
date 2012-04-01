#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import sys, os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import datetime
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
        test_depends
from trytond.transaction import Transaction


class AccountInvoiceTestCase(unittest.TestCase):
    '''
    Test AccountInvoice module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_invoice')
        self.payment_term = POOL.get('account.invoice.payment_term')
        self.currency = POOL.get('currency.currency')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('account_invoice')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010payment_term(self):
        '''
        Test payment_term.
        '''
        with Transaction().start(DB_NAME, USER, CONTEXT) as transaction:
            cu1_id = self.currency.create({
                    'name': 'cu1',
                    'symbol': 'cu1',
                    'code': 'cu1'
                    })
            cu1 = self.currency.browse(cu1_id)

            term_id = self.payment_term.create({
                    'name': '30 days, 1 month, 1 month + 15 days',
                    'lines': [
                        ('create', {
                                'sequence': 0,
                                'type': 'percent',
                                'divisor': 4,
                                'percentage': 25,
                                'days': 30,
                                }),
                        ('create', {
                                'sequence': 1,
                                'type': 'percent_on_total',
                                'divisor': 4,
                                'percentage': 25,
                                'months': 1,
                                }),
                        ('create', {
                                'sequence': 2,
                                'type': 'fixed',
                                'months': 1,
                                'days': 30,
                                'amount': Decimal('396.84'),
                                'currency': cu1_id,
                                }),
                        ('create', {
                                'sequence': 3,
                                'type': 'remainder',
                                'months': 2,
                                'days': 30,
                                'day': 15,
                                })]
                    })
            term = self.payment_term.browse(term_id)
            terms = term.compute(Decimal('1587.35'), cu1, term,
                    date=datetime.date(2011,10,1))
            self.assertEqual(terms, [
                    (datetime.date(2011,10,31), Decimal('396.84')),
                    (datetime.date(2011,11,01), Decimal('396.84')),
                    (datetime.date(2011,12,01), Decimal('396.84')),
                    (datetime.date(2012,01,14), Decimal('396.83')),
                    ])



def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
