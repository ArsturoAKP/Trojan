"""Your test suite. Write smoke, regression, and slow tests here.

Every test MUST carry exactly one marker (@pytest.mark.smoke / regression /
slow) and name its author in the docstring, e.g.:

    @pytest.mark.smoke
    def test_login_works():
        '''Author: <name>. Smoke test for login.'''

Run:  pytest            (all)     pytest -m smoke     pytest -m regression
"""
import pytest
from bookstore_app import Users, Catalog, Cart



# ---- OUR SMOKE TESTS (at least 5) ----
@pytest.mark.smoke
def test_smoke_register_new_user():
    """Author: <Name>. Smoke: a brand-new user can register and is stored."""
    users = Users()
    assert users.register("alice", "secret123") is True
    assert "alice" in users.users

@pytest.mark.smoke
def test_smoke_login_correct_and_wrong_password():
    """Author: <Name>. Smoke: login accepts the right password and rejects a wrong one."""
    users = Users()
    users.register("bob", "pass123")
    assert users.login("bob", "pass123") is True
    assert users.login("bob", "wrongpass") is False

@pytest.mark.smoke
def test_smoke_add_product_is_saved():
    """Author: <Name>. Smoke: an added product is stored in the catalog."""
    cat = Catalog()
    cat.add_product("B1", "Python Basics", 20)
    assert cat.products["B1"] == {"title": "Python Basics", "price": 20}
    assert cat.search("Python") == ["B1"]

@pytest.mark.smoke
def test_smoke_add_to_cart():
    """Author: <Name>. Smoke: a known product reaches the cart."""
    cat = Catalog()
    cat.add_product("B1", "Python Basics", 20)
    cart = Cart(cat)
    assert cart.add("B1") is True
    assert cart.items == ["B1"]

@pytest.mark.smoke
def test_smoke_checkout_non_empty_cart():
    """Author: <Name>. Smoke: checkout of a non-empty cart returns the order and records it."""
    cat = Catalog()
    cat.add_product("B1", "Python Basics", 20)
    cart = Cart(cat)
    cart.add("B1")
    order = cart.checkout()
    assert order == ["B1"]
    assert cart.history() == [["B1"]]
    assert cart.items == []

@pytest.mark.smoke
def test_smoke_remove_from_cart():
    """Author: <Name>. Smoke: an item in the cart can be removed again."""
    cat = Catalog()
    cat.add_product("B1", "Python Basics", 20)
    cart = Cart(cat)
    cart.add("B1")
    assert cart.remove("B1") is True
    assert cart.items == []


@pytest.mark.smoke
def test_smoke_duplicate_and_unknown_are_rejected():
    """Author: <Name>. Smoke: a taken username and an unknown product are rejected."""
    users = Users()
    assert users.register("alice", "secret123") is True
    assert users.register("alice", "other456") is False
    cart = Cart(Catalog())
    assert cart.add("NOPE") is False
    assert cart.items == []

# ---- OUR REGRESSION TESTS (the bug hunt) ----
@pytest.mark.regression
def test_cart_total_includes_last_item():
    """Author: <Name>. Regression: Cart.total().
    Wrong: with items priced 10, 15 and 25 in the cart, total() returns 25
    (the last item is skipped; one item gives 0).
    Correct: total() returns the sum of every item in the cart, 50."""
    cat = Catalog()
    cat.add_product("A", "Alpha", 10)
    cat.add_product("B", "Beta", 15)
    cat.add_product("C", "Gamma", 25)
    cart = Cart(cat)
    for pid in ("A", "B", "C"):
        cart.add(pid)
    assert cart.total() == 50

@pytest.mark.regression
def test_import_products_returns_number_imported():
    """Author: <Name>. Regression: Cart.import_products().
    Wrong: importing 2 products returns 3 (count is off by one).
    Correct: returns how many were imported, 2."""
    cat = Catalog()
    cart = Cart(cat)
    assert cart.import_products([("A", "Alpha", 5), ("B", "Beta", 6)]) == 2
    assert len(cat.products) == 2

@pytest.mark.regression
def test_checkout_empty_cart_returns_none():
    """Author: <Name>. Regression: Cart.checkout().
    Wrong: checking out an empty cart returns [] and records an empty order,
    so history() becomes [[]].
    Correct: per the docstring it returns None, and no order is recorded."""
    cart = Cart(Catalog())
    assert cart.checkout() is None
    assert cart.history() == []

@pytest.mark.regression
def test_search_is_case_insensitive():
    """Author: <Name>. Regression: Catalog.search().
    Wrong: search("python") returns [] for the title "Python Testing".
    Correct: a keyword search finds the title regardless of letter case, [1]."""
    cat = Catalog()
    cat.add_product(1, "Python Testing", 30)
    assert cat.search("python") == [1]
    assert cat.search("TESTING") == [1]

# ---- OUR SLOW TESTS (at least 2) ----
@pytest.mark.slow
def test_slow_bulk_import_and_search():
    """Author: <Name>. Slow: imports 100,000 products, then searches them."""
    # Slow because it builds and imports 100,000 products (import_products
    # sleeps once per product) and then scans the whole catalogue several
    # times with search(), which checks every title on each call.
    cat = Catalog()
    cart = Cart(cat)
    products = [(f"P{i}", f"Book number {i}", i % 50 + 1) for i in range(100_000)]
    cart.import_products(products)
    assert len(cat.products) == 100_000
    assert cat.products["P99999"]["title"] == "Book number 99999"
    # 200 searches x 100,000 titles = 20,000,000 title comparisons
    for i in range(0, 100_000, 500):
        assert f"P{i}" in cat.search(f"Book number {i}")

@pytest.mark.slow
def test_slow_many_cart_operations():
    """Author: <Name>. Slow: 600,000 add/remove operations plus 600 checkouts."""
    # Slow because it runs hundreds of thousands of cart operations in a loop;
    # remove() also scans the item list each time.
    cat = Catalog()
    for i in range(100):
        cat.add_product(f"P{i}", f"Title {i}", 10)
    cart = Cart(cat)
    for i in range(600_000):
        cart.add(f"P{i % 100}")
        if i % 2 == 0:
            cart.remove(f"P{i % 100}")
        if i % 1000 == 999:
            cart.checkout()
    assert len(cart.history()) == 600
    assert all(len(order) == 500 for order in cart.history())

@pytest.mark.slow
def test_slow_many_users_register_and_login():
    """Author: <Name>. Slow: registers 300,000 users and logs each one in."""
    # Slow because it performs 300,000 registrations followed by 600,000
    # login attempts (one correct and one wrong password per user).
    users = Users()
    n = 300_000
    for i in range(n):
        assert users.register(f"user{i}", f"pass{i}") is True
    assert len(users.users) == n
    for i in range(n):
        assert users.login(f"user{i}", f"pass{i}") is True
        assert users.login(f"user{i}", f"wrong{i}") is False


@pytest.mark.slow
def test_slow_repeated_search_large_catalog():
    """Author: <Name>. Slow: 1,500 searches over a 20,000-product catalogue."""
    # Slow because search() scans every title on each call:
    # 1,500 searches x 20,000 titles = 30,000,000 title comparisons.
    cat = Catalog()
    for i in range(20_000):
        cat.add_product(i, f"Book {i} Volume", 10)
    for i in range(1_500):
        results = cat.search(f"Book {i} ")
        assert results == [i]
    assert len(cat.search("Volume")) == 20_000


@pytest.mark.slow
def test_slow_many_checkouts_build_history():
    """Author: <Name>. Slow: 1,000,000 checkouts of 3-item orders."""
    # Slow because it fills and checks out the cart 1,000,000 times, building an
    # order history of 1,000,000 orders (3,000,000 items in total).
    cat = Catalog()
    for pid in ("A", "B", "C"):
        cat.add_product(pid, f"Title {pid}", 10)
    cart = Cart(cat)
    for _ in range(1_000_000):
        cart.add("A"); cart.add("B"); cart.add("C")
        assert cart.checkout() == ["A", "B", "C"]
    assert len(cart.history()) == 1_000_000
    assert cart.items == []