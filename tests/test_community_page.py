from pages.community_page import CommunityPage


def test_community_page_loaded(page):
    community_page = CommunityPage(page).open()
    community_page.expect_loaded()
