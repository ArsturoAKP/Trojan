# FINDINGS.md -- Bug-hunt log

Group: Trojan
Members: Thin Thiri Zaw, Paing Oo Thant, L Peter San Awng, Kaung Myat Tun, Aung Kyaw Phyo

Each bug was found test-first: the regression test was committed failing
against the shipped code, then the fix was committed separately.
Six defects were found; bugs 5 and 6 share one root cause and one fix, so
they are recorded together in Entry 5 (the brief allows five entries).

---

## Entry 1 -- `cart.py` -> `Cart.total()`
- **Suspected:** The loop is `for i in range(len(self.items) - 1)`. For three
  items that is `range(2)`, so index 2 -- the last item -- is never added.
  The docstring promises the "total price of everything currently in the cart".
- **Tried:** Added products A = 10, B = 15, C = 25, put all three in a cart
  and called `cart.total()`. Test: `test_cart_total_includes_last_item`.
- **Observed:**
  ```text
  >>> cart.total()
  25
  FAILED tests/test_bookstore.py::test_cart_total_includes_last_item - assert 25 == 50
  ```
  Only 10 + 15 was counted; with a single item `total()` returns `0`.
- **Expected:** `50` (10 + 15 + 25), because the docstring says *everything*
  in the cart is totalled.
- **Fixed:** Replaced the index loop with `for pid in self.items:`.
  Test commit `252f0af`, fix commit `1eeb31e`.
- **Author:** <Name>

---

## Entry 2 -- `cart.py` -> `Cart.import_products()`
- **Suspected:** The method ends with `return count + 1`, although `count`
  is already increased once per product. The docstring says it "returns how
  many were imported".
- **Tried:** Imported two products and compared the return value with the
  catalogue size. Test: `test_import_products_returns_number_imported`.
- **Observed:**
  ```text
  >>> cart.import_products([("A", "Alpha", 5), ("B", "Beta", 6)])
  3
  >>> len(cat.products)
  2
  FAILED ...::test_import_products_returns_number_imported - AssertionError: assert 3 == 2
  ```
  The products are stored correctly; only the reported number is wrong.
- **Expected:** `2`, the number of products actually imported.
- **Fixed:** Changed `return count + 1` to `return count`.
  Test commit `75dbbfe`, fix commit `96ab32b`.
- **Author:** <Name>

---

## Entry 3 -- `cart.py` -> `Cart.checkout()`
- **Suspected:** The docstring says it returns the order list "**or None if
  the cart is empty**", but the code has no `if` -- nothing checks for an
  empty cart.
- **Tried:** Checked out a brand-new, empty cart and looked at the history.
  Test: `test_checkout_empty_cart_returns_none`.
- **Observed:**
  ```text
  >>> cart = Cart(Catalog())
  >>> cart.checkout()
  []
  >>> cart.history()
  [[]]
  FAILED ...::test_checkout_empty_cart_returns_none - assert [] is None
  ```
  It returned `[]` and also recorded an empty order in the history.
- **Expected:** `None`, as the docstring states, and no order recorded --
  `history()` should stay `[]`. An empty "order" should never be placed.
- **Fixed:** Added `if not self.items: return None` at the top of
  `checkout()`, before anything is recorded.
  Test commit `18160b3`, fix commit `59a64ac`.
- **Author:** <Name>

---

## Entry 4 -- `catalog.py` -> `Catalog.search()`
- **Suspected:** The match is `keyword in info["title"]`, which compares
  letters exactly, so capitalisation matters.
- **Tried:** Added "Python Testing" and searched with different letter cases.
  We first tried the exact title and `"Python"`, which both worked, so we then
  tried lower and upper case. Test: `test_search_is_case_insensitive`.
- **Observed:**
  ```text
  >>> cat.search("Python")
  [1]
  >>> cat.search("python")
  []
  >>> cat.search("TESTING")
  []
  FAILED ...::test_search_is_case_insensitive - assert [] == [1]
  ```
- **Expected:** `[1]` for all three. "python" and "Python" are the same word,
  customers often type in lower case, and a bookstore search that cannot find
  "Python Testing" from "python" is broken for its users. (Unlike a made-up
  rule such as "at most ten results", this follows directly from what a
  keyword search is for.)
- **Fixed:** Compare both sides in lower case:
  `keyword.lower() in info["title"].lower()`. Stored titles are unchanged.
  Test commit `6133602`, fix commit `974199c`.
- **Author:** <Name>

---

## Entry 5 -- `users.py` -> `Users.login()` (bugs 5 and 6)
- **Suspected:** `login()` builds `cleaned = "".join(ch for ch in password if ch.isalnum())`,
  removing every symbol from the typed password, while `register()` stores
  the password unchanged. The two sides are treated differently.
- **Tried:** (a) registered `carol` / `p@ss!word` and logged in with the same
  password; (b) registered `dave` / `secret1` and logged in with wrong
  passwords that differ only by symbols. Tests:
  `test_login_accepts_password_with_symbols`,
  `test_login_rejects_password_with_extra_symbols`.
- **Observed:**
  ```text
  >>> u.login("carol", "p@ss!word")
  False
  >>> u.login("dave", "secret1!")
  True
  >>> u.login("dave", "se-cret1")
  True
  >>> u.login("dave", "wrongpw")
  False
  ```
  Bug 5: the correct password is rejected. Bug 6: wrong passwords are
  accepted -- a security hole. A plain wrong password like `"wrongpw"` is
  still rejected, which is why this bug is easy to miss.
- **Expected:** `True` for (a), `False` for both wrong passwords in (b). The
  docstring says login succeeds only if "the password matches", meaning
  exactly.
- **Fixed:** Removed the cleaning line and compare exactly:
  `return stored is not None and stored == password`.
  Test commit `3af793b`, fix commit `b269e1c`.
- **Author:** <Name>