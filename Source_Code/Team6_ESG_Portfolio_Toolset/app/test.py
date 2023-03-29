import unittest
import os
import pandas as pd
import main

class TestESGPortfolio(unittest.TestCase):

    def testAddToPortfolioList(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
        main.add_to_portfolio_list("AppTestPortfolio")
        portfoliolist = pd.read_csv(portfolio_file)
        actual = len(portfoliolist)
        self.assertEqual(4, actual, "Test Failed")

if __name__ == '__main__':
    unittest.main()