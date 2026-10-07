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


## Part F -- Team reflection
1. Why is running only regression tests before every commit inefficient?
2. Why do smoke tests usually run first in a CI/CD pipeline?
3. What risks arise if slow tests are never run?
4. Can one test belong to two categories? Give an example.
5. Bug-finders and bug-fixers are often different people in a real QA team.
   What does that separation change about how a bug report must be written?
