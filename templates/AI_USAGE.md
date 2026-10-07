# AI_USAGE.md -- Declaration and audit

Group: Trojan   Members: Thin Thiri Zaw, Paing Oo Thant, L Peter San Awng, Kaung Myat Tun, Aung Kyaw Phyo

## D3.1 Declaration (required)

| AI tool | How we used it |
|---|---|
| Claude (claude.ai) | Step-by-step explanation of the assignment; draft smoke, slow and regression tests; suggested bug fixes; structure of REPORT.md, FINDINGS.md and this file; CI workflow. **Outcome: modified and verified.** Every smoke and slow test was run on the shipped code (all passed); every regression test was run on the shipped code and confirmed to fail for the expected reason before it was committed; each fix was committed separately and the full suite re-run (18 passed). |
| <other tool, if any member used one> | <what for, and whether accepted / modified / rejected> |

## D3.2 Audit of the supplied ai_review/ test set (graded core)

File: `ai_review/test_ai_generated.py`. Each test was run against the
**shipped** application (commit `cf5ca64`) and, as a cross-check, against our
**fixed** application (commit `b269e1c`).

Commands:
```text
git checkout cf5ca64 -- bookstore_app/
python -m pytest ai_review/test_ai_generated.py -v     (saved as evidence_ai_shipped.txt)
git checkout HEAD -- bookstore_app/
python -m pytest ai_review/test_ai_generated.py -v     (saved as evidence_ai_fixed.txt)
```

| Test | What it claims to catch | Does it actually? | Evidence (shipped -> fixed) | Verdict |
|---|---|---|---|---|
| test_cart_total_sums_items | cart total is wrong | **Yes** -- catches `Cart.total()` skipping the last item | FAILED `assert 10 == 30` -> PASSED | genuine |
| test_login_rejects_wrong_password | wrong password is accepted | **No** -- `"wrongpw"` has no symbols, so the symbol-stripping bug is never triggered | PASSED -> PASSED | passes anyway |
| test_search_finds_exact_title | search cannot find a product | **No** -- exact-case title never triggers the case-sensitivity bug | PASSED -> PASSED | passes anyway |
| test_import_returns_count | import count is wrong | **Yes** -- catches `return count + 1` | FAILED `assert 3 == 2` -> PASSED | genuine |
| test_register_duplicate_returns_false | duplicate registration is allowed | **No** -- `register()` has no bug here | PASSED -> PASSED | passes anyway |
| test_checkout_empty_returns_none | empty checkout does not return None | **Yes** -- catches the missing empty-cart check (but not the empty order in `history()`) | FAILED `assert [] is None` -> PASSED | genuine |
| test_add_to_cart_returns_true_for_known_product | known product cannot be added | **No** -- `add()` has no bug; only the return value is checked | PASSED -> PASSED | passes anyway |
| test_search_is_limited_to_ten_results | search returns more than ten results | **No** -- no ten-result limit exists in the docstring or assignment | FAILED `assert 20 <= 10` -> FAILED `assert 20 <= 10` | invented bug |

**Totals:** 3 genuine, 4 passes anyway, 1 invented bug.

### Evidence -- shipped code (`evidence_ai_shipped.txt`)
```text
ai_review/test_ai_generated.py::test_cart_total_sums_items FAILED        [ 12%]
ai_review/test_ai_generated.py::test_login_rejects_wrong_password PASSED [ 25%]
ai_review/test_ai_generated.py::test_search_finds_exact_title PASSED     [ 37%]
ai_review/test_ai_generated.py::test_import_returns_count FAILED         [ 50%]
ai_review/test_ai_generated.py::test_register_duplicate_returns_false PASSED [ 62%]
ai_review/test_ai_generated.py::test_checkout_empty_returns_none FAILED  [ 75%]
ai_review/test_ai_generated.py::test_add_to_cart_returns_true_for_known_product PASSED [ 87%]
ai_review/test_ai_generated.py::test_search_is_limited_to_ten_results FAILED [100%]

>       assert c.total() == 30
E       assert 10 == 30
>       assert c.import_products([(1, "A", 5), (2, "B", 6)]) == 2
E       AssertionError: assert 3 == 2
>       assert Cart(Catalog()).checkout() is None
E       assert [] is None
>       assert len(cat.search("match")) <= 10
E       AssertionError: assert 20 <= 10
========================= 4 failed, 4 passed in 0.08s =========================
```

### Evidence -- fixed code (`evidence_ai_fixed.txt`)
```text
<paste your real output here>
```

### Why each verdict

- **test_cart_total_sums_items -- genuine.** Shipped `total()` returned 10 for
  items priced 10 and 20 because the loop skips the last item; after our fix
  it returns 30 (FINDINGS Entry 1).
- **test_login_rejects_wrong_password -- passes anyway.** The shipped `login()`
  strips symbols, but `"wrongpw"` contains none, so it is correctly rejected.
  On the same shipped code `login("dave", "secret1!")` returned `True` for the
  password `"secret1"` (FINDINGS Entry 5). The test needed a wrong password
  that differs only by a symbol, e.g. `"secret1!"`.
- **test_search_finds_exact_title -- passes anyway.** It searches the exact
  title in the exact case, which the case-sensitive shipped `search()` handles.
  `search("python")` returned `[]` on the same code (FINDINGS Entry 4).
- **test_import_returns_count -- genuine.** Shipped code returned 3 for two
  products (`count + 1`); after our fix it returns 2 (FINDINGS Entry 2).
- **test_register_duplicate_returns_false -- passes anyway.** `register()`
  already rejects a taken username; there is no planted bug to detect.
- **test_checkout_empty_returns_none -- genuine.** Shipped code returned `[]`;
  after our fix it returns `None` (FINDINGS Entry 3). Weaker than our own test:
  it does not check that `history()` stays empty.
- **test_add_to_cart_returns_true_for_known_product -- passes anyway.** `add()`
  has no planted bug, and the test only checks the return value, not that the
  item is in `cart.items`.
- **test_search_is_limited_to_ten_results -- invented bug.** `search()`'s
  docstring says it returns the products "whose title contains the keyword" --
  all of them. Nothing mentions a limit of ten. All 20 products titled
  "match" really match, so 20 is correct; the test fails on both the shipped
  and the fixed code.

## D3.3 Verdict

**Which failure mode was most common?** "Passes anyway": 4 of the 8 tests
passed on the shipped, buggy code and therefore detected nothing. Only 3 of 8
genuinely caught a planted bug, and 1 invented a ten-result limit. The pattern
was easy inputs that never reach the bug (`"wrongpw"` has no symbols; the
search used the exact case) or tests of functions that had no bug (`register()`,
`add()`). The set also missed both harder defects we found: case-sensitive
search and the login symbol bug.

**Why is a test that passes against buggy code more dangerous than one that
crashes?** A crashing or failing test turns the build red, so someone
investigates. A green test reports safety that does not exist.
`test_login_rejects_wrong_password` is green on the shipped code and its name
says wrong passwords are rejected, yet on that same code
`login("dave", "secret1!")` returned `True`. A team trusting it would ship a
login that accepts wrong passwords.

**What will we check in future before trusting a generated test?** Run it on
the buggy and the fixed code and compare the results (this exposed the four
"passes anyway" tests); check every requirement against the docstring (this
showed the ten-result limit was invented); ask which input would trigger the
bug and whether the test uses it (symbols for login, lower case for search);
check side effects such as `history()`, not only return values; and never
trust a test because its name sounds right.