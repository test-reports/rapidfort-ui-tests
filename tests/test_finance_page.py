from pages.solution.by_industry.finance_page import FinancePage


def test_finance_page_loaded(page):
    finance_page = FinancePage(page)

    finance_page.open("solutions/by-industry/finance")
    finance_page.expect_loaded()
