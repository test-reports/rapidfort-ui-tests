from pages.resources.blog_page import BlogPage


def test_blog_page_loaded(page):
    blog_page = BlogPage(page).open()
    blog_page.expect_loaded()
