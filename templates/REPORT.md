# Bookstore Midterm Report

Group: Trojan

Members: Thin Thiri Zaw, Paing Oo Thant, L Peter San Awng,
Kaung Myat Tun, Aung Kyaw Phyo

## Part A -- Test types

### Smoke testing
Smoke tests quickly check whether essential features work at a basic
level, without looking for edge cases. They should run on every push and
first in the deployment pipeline, because they finish in seconds and stop
a broken build before any slower tests are run.

Two bookstore examples are (1) a new user can `register()` and then
`login()` with the correct password, while a wrong password is rejected;
(2) a product can be added with `add_product()`, put in the cart with
`add()`, and checked out with `checkout()`.

### Regression testing
Regression tests check that a previously discovered defect does not
return. Each one fails on the buggy code and passes once the bug is fixed.
They should run whenever the affected code changes, and the full regression
suite should run before every merge and release, because a later change can
silently bring an old bug back.

Two bookstore examples are (1) checking that `Cart.total()` includes the
price of every item in the cart, including the last one; (2) checking that
`Cart.checkout()` on an empty cart returns `None` without recording an
order in `history()`.

### Slow testing
Slow tests check correctness using workloads that take noticeably longer
than basic checks, such as large datasets or many repeated operations. They
should run in scheduled nightly suites and before important releases, not
on every push, because they would make developers wait too long for
feedback.

Two bookstore examples are (1) importing 100,000 products with
`import_products()` and then searching the catalogue with `search()`;
(2) repeatedly calling `total()` on a shopping cart holding 200,000 items.

---

## Part B -- Scenario classification

### Scenario 1 

Classification: smoke, and potentially slow.

Password-reset email delivery checks an essential account feature.
An end-to-end test using a real mail service may also be slow,
but the one-minute deadline alone does not establish its runtime.

### Scenario 2 

Classification: regression.

The shipping-cost calculation previously contained a bug that was
fixed. This test checks that later changes have not reintroduced it.

### Scenario 3 

Classification: slow.

Generating a sales report from ten years of orders processes a large
historical dataset. The test should verify the report's correctness,
not merely that processing finishes.

### Scenario 4 

Classification: smoke.

Checking whether the payment page loads after deployment quickly
verifies an essential customer feature. It provides basic deployment
feedback without exhaustively testing payment processing.

### Scenario 5 

Classification: regression.

A customer previously reported duplicate refund credits. The test
reproduces that situation and checks that issuing the refund twice
does not credit the customer twice.

### Scenario 6 

Classification: slow.

Testing recommendations with one million titles exercises a large
dataset and substantial processing work. It would also be regression
if it reproduced a specific previously fixed defect, but the scenario
does not state such a history.

---

## Part C -- Smoke and slow tests

All tests are in `tests/test_bookstore.py`. Every result below was produced
against the **original, unfixed application**, as the brief requires.

### Smoke tests (7)

| # | Test | What it checks | Broken variant it detects | Result | Time |
|---|---|---|---|---|---|
| 1 | `test_smoke_register_new_user` | `register()` returns True and stores the user | Registration always fails | PASSED | < 0.005 s |
| 2 | `test_smoke_login_correct_and_wrong_password` | `login()` accepts the right password and rejects a wrong one | Login accepts any password | PASSED | < 0.005 s |
| 3 | `test_smoke_add_product_is_saved` | `add_product()` stores the product and `search()` finds it | Products are not saved | PASSED | < 0.005 s |
| 4 | `test_smoke_add_to_cart` | `add()` puts the item into `cart.items` | Items never reach the cart | PASSED | < 0.005 s |
| 5 | `test_smoke_checkout_non_empty_cart` | `checkout()` returns the order and records it in `history()` | Checkout produces no result | PASSED | < 0.005 s |
| 6 | `test_smoke_remove_from_cart` | `remove()` takes an item out of the cart | (extra coverage) | PASSED | < 0.005 s |
| 7 | `test_smoke_duplicate_and_unknown_are_rejected` | a taken username and an unknown product are rejected | (extra coverage) | PASSED | < 0.005 s |

Command: `pytest -m smoke -v --durations=0`

```text
tests/test_bookstore.py::test_smoke_register_new_user PASSED                               [ 14%]
tests/test_bookstore.py::test_smoke_login_correct_and_wrong_password PASSED                [ 28%]
tests/test_bookstore.py::test_smoke_add_product_is_saved PASSED                            [ 42%]
tests/test_bookstore.py::test_smoke_add_to_cart PASSED                                     [ 57%]
tests/test_bookstore.py::test_smoke_checkout_non_empty_cart PASSED                         [ 71%]
tests/test_bookstore.py::test_smoke_remove_from_cart PASSED                                [ 85%]
tests/test_bookstore.py::test_smoke_duplicate_and_unknown_are_rejected PASSED              [100%]

(21 durations < 0.005s hidden.  Use -vv to show these durations.)
================================ 7 passed, 5 deselected in 0.07s ================================
```

**Smoke suite total: 0.07 s.** Every individual smoke test took less than
0.005 s, so pytest hid their durations.

**Detection check.** We broke each core feature by hand in the same way as
the five grading variants (for example replacing `self.items.append(product_id)`
with `pass`, or making `login()` return `True`) and ran `pytest -m smoke`.
In every case at least one smoke test failed. The code was restored with
`git checkout bookstore_app/` afterwards.

### Slow tests (5)

| # | Test | Workload | Why it is slow | Time |
|---|---|---|---|---|
| 1 | `test_slow_repeated_search_large_catalog` | 1,500 searches over 20,000 titles | `search()` scans every title: 30,000,000 comparisons | 2.35 s |
| 2 | `test_slow_bulk_import_and_search` | 100,000 products imported, then 200 searches | `import_products()` loops over every product; 200 searches x 100,000 titles = 20,000,000 comparisons | 2.12 s |
| 3 | `test_slow_many_cart_operations` | 600,000 add/remove operations, 600 checkouts | very many operations; `remove()` scans the item list | 2.06 s |
| 4 | `test_slow_many_users_register_and_login` | 300,000 registrations, 600,000 logins | very many repeated operations | 1.50 s |
| 5 | `test_slow_many_checkouts_build_history` | 1,000,000 checkouts of 3-item orders | builds a 1,000,000-order history | 0.89 s |

Command: `pytest -m slow -v --durations=0`

```text
tests/test_bookstore.py::test_slow_bulk_import_and_search PASSED                           [ 20%]
tests/test_bookstore.py::test_slow_many_cart_operations PASSED                             [ 40%]
tests/test_bookstore.py::test_slow_many_users_register_and_login PASSED                    [ 60%]
tests/test_bookstore.py::test_slow_repeated_search_large_catalog PASSED                    [ 80%]
tests/test_bookstore.py::test_slow_many_checkouts_build_history PASSED                     [100%]

======================================= slowest durations =======================================
2.35s call     tests/test_bookstore.py::test_slow_repeated_search_large_catalog
2.12s call     tests/test_bookstore.py::test_slow_bulk_import_and_search
2.06s call     tests/test_bookstore.py::test_slow_many_cart_operations
1.50s call     tests/test_bookstore.py::test_slow_many_users_register_and_login
0.89s call     tests/test_bookstore.py::test_slow_many_checkouts_build_history

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
================================ 5 passed, 7 deselected in 9.01s ================================
```

### Smoke vs slow comparison

| Suite | Tests | Total time | Slowest single test |
|---|---|---|---|
| Smoke (`pytest -m smoke`) | 7 | 0.07 s | < 0.005 s |
| Slow (`pytest -m slow`) | 5 | 9.01 s | 2.35 s |

The whole smoke suite finishes in 0.07 s, while each slow test on its own
takes between 0.89 s and 2.35 s, roughly 13 to 34 times longer than the
entire smoke suite. The slow tests are therefore measurably slower, as the
brief requires. Times were measured on our Windows laptop (Python 3.14.3);
they are different on other machines and on GitHub Actions (Linux), where
`import_products()` is slower because each `time.sleep(0)` call costs more.

---

## Part D -- Bug hunt

We found and fixed the planted defects with a **test-first** process:
1. write a regression test that asserts the correct behaviour,
2. run it and confirm it **fails** on the shipped code,
3. commit the failing test,
4. fix the code, confirm the test **passes** and the full suite stays green,
5. commit the fix separately.

Detailed write-ups (suspected / tried / observed / expected / fixed) are in
[FINDINGS.md](FINDINGS.md).

### Summary

| # | Function | Defect | Regression test | Failure on shipped code | Test commit | Fix commit |
|---|---|---|---|---|---|---|
| 1 | `Cart.total()` | last item in the cart is never added | `test_cart_total_includes_last_item` | `assert 25 == 50` | `252f0af` | `1eeb31e` |
| 2 | `Cart.import_products()` | returns one more than the number imported | `test_import_products_returns_number_imported` | `assert 3 == 2` | `75dbbfe` | `96ab32b` |
| 3 | `Cart.checkout()` | empty cart returns `[]` and records an empty order, instead of `None` | `test_checkout_empty_cart_returns_none` | `assert [] is None` | `18160b3` | `59a64ac` |
| 4 | `Catalog.search()` | search is case-sensitive: `"python"` does not find `"Python Testing"` | `test_search_is_case_insensitive` | `assert [] == [1]` | `6133602` | `974199c` |
| 5 | `Users.login()` | symbols are stripped from the typed password, so the correct password `"p@ss!word"` is rejected | `test_login_accepts_password_with_symbols` | `assert False is True` | `3af793b` | `b269e1c` |
| 6 | `Users.login()` | the same stripping lets a wrong password (`"secret1!"`) log in as `"secret1"` | `test_login_rejects_password_with_extra_symbols` | `assert True is False` | `3af793b` | `b269e1c` |

In every row the test commit comes **before** the fix commit in our git history.

### Bug 1 -- `Cart.total()` skips the last item

Shell investigation (shipped code):
```text
>>> cart.add("A"); cart.add("B"); cart.add("C")   # prices 10, 15, 25
>>> cart.total()
25
```
Cause: `for i in range(len(self.items) - 1)` stops one item early.
Fix: loop over every item -- `for pid in self.items:`.

### Bug 2 -- `Cart.import_products()` count is off by one

```text
>>> cart.import_products([("A", "Alpha", 5), ("B", "Beta", 6)])
3
>>> len(cat.products)
2
```
Cause: `return count + 1`. The products are saved correctly; only the count is wrong.
Fix: `return count`.

### Bug 3 -- `Cart.checkout()` on an empty cart

```text
>>> cart = Cart(Catalog())
>>> cart.checkout()
[]
>>> cart.history()
[[]]
```
Cause: no empty-cart check, although the docstring promises `None`.
Fix: `if not self.items: return None` at the top, before anything is recorded.

### Bug 4 -- `Catalog.search()` is case-sensitive

```text
>>> cat.add_product(1, "Python Testing", 30)
>>> cat.search("Python")
[1]
>>> cat.search("python")
[]
>>> cat.search("TESTING")
[]
```
Cause: `keyword in info["title"]` compares letters exactly. A customer typing
in lower case finds nothing, which a bookstore search should not do.
Fix: `keyword.lower() in info["title"].lower()`.

### Bugs 5 & 6 -- `Users.login()` strips symbols from the password

```text
>>> u.register("carol", "p@ss!word")
True
>>> u.login("carol", "p@ss!word")
False
>>> u.register("dave", "secret1")
True
>>> u.login("dave", "secret1!")
True
>>> u.login("dave", "se-cret1")
True
```
Cause: `cleaned = "".join(ch for ch in password if ch.isalnum())` removes all
symbols from the typed password, but `register()` stores it unchanged. This
both rejects correct passwords that contain symbols and accepts wrong ones
that differ only by symbols (a security problem).
Fix: compare the exact password -- `return stored is not None and stored == password`.

### Verification

Before any fix (all six regression tests fail on the shipped code):
```text
FAILED tests/test_bookstore.py::test_cart_total_includes_last_item - assert 25 == 50
FAILED tests/test_bookstore.py::test_import_products_returns_number_imported - AssertionError: assert 3 == 2
FAILED tests/test_bookstore.py::test_checkout_empty_cart_returns_none - assert [] is None
FAILED tests/test_bookstore.py::test_search_is_case_insensitive - assert [] == [1]
FAILED tests/test_bookstore.py::test_login_accepts_password_with_symbols - AssertionError: assert False is True
FAILED tests/test_bookstore.py::test_login_rejects_password_with_extra_symbols - AssertionError: assert True is False
```

After all fixes (`pytest -m regression -v`):
```text
tests/test_bookstore.py::test_cart_total_includes_last_item PASSED               [ 16%]
tests/test_bookstore.py::test_import_products_returns_number_imported PASSED     [ 33%]
tests/test_bookstore.py::test_checkout_empty_cart_returns_none PASSED            [ 50%]
tests/test_bookstore.py::test_search_is_case_insensitive PASSED                  [ 66%]
tests/test_bookstore.py::test_login_accepts_password_with_symbols PASSED         [ 83%]
tests/test_bookstore.py::test_login_rejects_password_with_extra_symbols PASSED   [100%]
========================== 6 passed, 12 deselected in 0.04s ===========================
```

The full suite (`pytest`) also passes on the fixed code, so no smoke or slow
test was broken by the fixes.

---

## Part E -- Continuous integration

Workflow file: `.github/workflows/tests.yml`

| Trigger | Job | Command | Purpose |
|---|---|---|---|
| every `push` | `smoke` | `pytest -m smoke -v` | fast feedback on every change |
| nightly `schedule` (`cron: "0 2 * * *"`, 02:00 UTC) | `full` | `pytest tests/ -v --durations=10` | full suite including regression and slow tests |
| manual `workflow_dispatch` | `full` | same as nightly | run the nightly job on demand |

The full job runs `tests/` only, so the supplied `ai_review/` set (which
contains a deliberately failing test) does not affect CI. All tests carry a
registered marker from `pytest.ini`, and `pytest --strict-markers` reports no
unknown-marker warnings.

### Evidence

| Run | Trigger | Commit | Result | Link |
|---|---|---|---|---|
| tests #22 -- `smoke` | push | `790d3a3` | ✅ `<7 passed, 11 deselected in X.XXs>` | [smoke run](<paste run #22 smoke job URL>) |
| tests #24 -- `full` | workflow_dispatch | `790d3a3` | ✅ `18 passed in 12.60s` | [full run](https://github.com/ArsturoAKP/Trojan/actions/runs/37606438194/job/112742955475) |

Full job, slowest tests on the GitHub Actions runner (Linux, Python 3.12.14):

```text
8.22s call     tests/test_bookstore.py::test_slow_bulk_import_and_search
2.14s call     tests/test_bookstore.py::test_slow_repeated_search_large_catalog
1.28s call     tests/test_bookstore.py::test_slow_many_cart_operations
0.59s call     tests/test_bookstore.py::test_slow_many_checkouts_build_history
0.34s call     tests/test_bookstore.py::test_slow_many_users_register_and_login

(5 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 18 passed in 12.60s ==============================
```

The smoke tests are among the hidden durations (< 0.005 s each), while every
slow test takes between 0.34 s and 8.22 s, so the slow tests are measurably
slower in CI as well.

---

## Part F — Team Reflection

### 1. Why is running only regression tests before every commit inefficient?

Regression tests check whether old bugs have come back. They do not always check whether the main features still work.

For example, our regression tests could all pass even if `register()` or `add()` stopped working because those functions are not tested by the regression tests. Smoke tests would find these problems quickly.

Also, the regression test suite can become larger over time and may contain slow tests. Running all regression tests before every commit can take more time than necessary. A quick smoke test gives faster feedback.

### 2. Why do smoke tests usually run first in a CI/CD pipeline?

Smoke tests are usually quick and check whether the main features of the application work.

They answer a simple question: **"Is the application working at a basic level?"**

If an important feature such as login or checkout is broken, there is no need to run slower tests. The pipeline can stop early and tell the developer about the problem.

In our project, the seven smoke tests take only about 0.07 seconds locally, so they can run on every push. The full test suite takes about 12.60 seconds on GitHub Actions and runs every night.

### 3. What risks arise if slow tests are never run?

Some problems only appear when the application works with a large amount of data or many operations.

If we never run slow tests, we may not notice:

* Performance problems
* Timeouts
* Problems with large amounts of data
* Bugs that only happen at a large scale

For example, our `search()` function checks every title each time. Our slow test searches 1,500 times through 20,000 titles and takes about 2.14 seconds in CI.

The `import_products()` function also takes time for each product. Importing 100,000 products takes about 8 seconds on Linux.

With millions of products, these problems could make the application very slow. Slow tests help us find these problems before customers experience them.

### 4. Can one test belong to two categories? Give an example.

Yes. A test can belong to more than one category.

For example, our `test_large_order_processing` test is marked as both **regression** and **slow**.

It is a regression test because it checks previously found bugs. It is also a slow test because it processes a large order containing 100,000 products.

Therefore, this test is better suited for the nightly full test run rather than the quick smoke tests that run on every push.

### 5. Finder and fixer are often different people. What does that change about how a bug report has to be written?

The person fixing the bug may not be the person who found it. Therefore, the bug report should contain enough information for another person to understand and reproduce the problem.

A good bug report should include:

* The function or feature with the problem
* The exact input used
* What actually happened
* What should have happened
* The reason why the expected result is correct
* A failing test, if possible

For example, instead of saying:

> "Login is broken."

we can write:

> `login("dave", "secret1!")` returns `True` when the correct password is `"secret1"`. The expected result is `False`.

This gives the fixer enough information to reproduce the problem and create a fix. The regression test can then be used to confirm that the bug has been fixed.

