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
For each of the six scenarios: smoke / regression / slow (may be more than one)
with a 2-3 sentence justification.

## Part F -- Team reflection
1. Why is running only regression tests before every commit inefficient?
2. Why do smoke tests usually run first in a CI/CD pipeline?
3. What risks arise if slow tests are never run?
4. Can one test belong to two categories? Give an example.
5. Bug-finders and bug-fixers are often different people in a real QA team.
   What does that separation change about how a bug report must be written?
