def test_blog_page_loaded(home_page):
    blog_page = home_page.go_to_blog()
    blog_page.expect_loaded()
