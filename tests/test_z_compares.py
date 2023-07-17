from z_compares import compare_macro_m_to_m, compare_order_volume, compare_technical,\
    compare_google_reddit_youtube, compare_news, compare_predicted_price


def test_compare_macro_m_to_m():
    assert compare_macro_m_to_m(-0.76) == (1.0, 0.0)
    assert compare_macro_m_to_m(-0.75) == (0.85, 0.15)
    assert compare_macro_m_to_m(-0.5) == (0.7, 0.3)
    assert compare_macro_m_to_m(-0.25) == (0.6, 0.4)
    assert compare_macro_m_to_m(0.0) == (0.6, 0.4)

    assert compare_macro_m_to_m(0.25) == (0.4, 0.6)
    assert compare_macro_m_to_m(0.5) == (0.3, 0.7)
    assert compare_macro_m_to_m(0.75) == (0.15, 0.85)
    assert compare_macro_m_to_m(0.76) == (0.0, 1.0)


def test_compare_order_volume():
    assert compare_order_volume(0.57, 0) == (0.7, 0.3)
    assert compare_order_volume(0, 0.57) == (0.3, 0.7)
    assert compare_order_volume(0, 0.60) == (0.2, 0.8)
    assert compare_order_volume(0, 0.63) == (0.1, 0.9)
    assert compare_order_volume(0, 0.57) == (0.3, 0.7)
    assert compare_order_volume(0.57, 0) == (0.7, 0.3)
    assert compare_order_volume(0.60, 0) == (0.8, 0.2)
    assert compare_order_volume(0.62, 0) == (0.9, 0.1)
    assert compare_order_volume(0.9, 0.48) == (1, 0.0)
    assert compare_order_volume(0.51, 0.48) == (0.0, 0.0)


def test_compare_predicted_price():
    assert compare_predicted_price(101, 100) == (0.6, 0.4)
    assert compare_predicted_price(100, 101) == (0.4, 0.6)
    assert compare_predicted_price(98, 100) == (0.3, 0.7)
    assert compare_predicted_price(100, 100) == (0.0, 0.0)

    assert compare_predicted_price(1009, 1000) == (0.0, 0.0)
    assert compare_predicted_price(1000, 1009) == (0.0, 0.0)

    assert compare_predicted_price(104, 100) == (0.9, 0.1)
    assert compare_predicted_price(105, 100) == (1.0, 0.0)

    assert compare_predicted_price(100, 104) == (0.1, 0.9)
    assert compare_predicted_price(100, 105) == (0.0, 1.0)

    assert compare_predicted_price(100, 103) == (0.2, 0.8)
    assert compare_predicted_price(100, 102) == (0.3, 0.7)


def test_compare_technical():
    assert compare_technical('up', True, True) == (1, 0)
    assert compare_technical('down', False, False) == (0, 1)


def test_compare_google_reddit_youtube():
    assert compare_google_reddit_youtube(100, 109) == (0.0, 0.0)
    assert compare_google_reddit_youtube(109, 100) == (0.0, 0.0)
    assert compare_google_reddit_youtube(110, 100) == (0.6, 0.4)
    assert compare_google_reddit_youtube(100, 110) == (0.4, 0.6)
    assert compare_google_reddit_youtube(124, 100) == (0.85, 0.15)
    assert compare_google_reddit_youtube(100, 124) == (0.15, 0.85)
    assert compare_google_reddit_youtube(115, 100) == (0.75, 0.25)
    assert compare_google_reddit_youtube(100, 115) == (0.25, 0.75)


def test_compare_news():
    assert compare_news(1, -1, 10000, 0) == (1, 0.0)
    assert compare_news(-1, 1.04, 0, 10000) == (0.0, 1)
    assert compare_news(1, -1, 10000, 0) == (1, 0.0)
    assert compare_news(-1, 1.04, 0, 10000) == (0.0, 1)
    assert compare_news(1, 1, 0, 10000) == (0.2, 0.8)
    assert compare_news(0, -1, 10000, 0) == (0.8, 0.2)
