Run `pytest tests/` from `/app` (default) for testing. Use `-s` for enabling output

[SV-Comp](https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks/-/tree/main/c/goblint-regression?ref_type=heads) style `.yml` file and place. Just make sure they have the property and are placed in the same directory as the target file.

### **1. Skip a Test (Always)**
Use `@pytest.mark.skip` to completely disable a test:
```python
import pytest

@pytest.mark.skip(reason="Skipping this test for now")
def test_skipped():
    assert False  # This will never run
```

---

### **2. Skip a Test Conditionally**
Use `@pytest.mark.skipif(condition, reason="...")` to disable based on conditions:
```python
import pytest
import sys

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_python_310_feature():
    assert True  # Runs only on Python 3.10+
```

---

### **3. Mark a Test as Expected to Fail**
Use `@pytest.mark.xfail` if a test is **expected to fail** but you don’t want it to cause a test failure:
```python
@pytest.mark.xfail(reason="Bug not fixed yet")
def test_known_bug():
    assert False  # Won't cause pytest to fail
```

---

### **4. Dynamically Skip a Test in Code**
You can use `pytest.skip()` inside a test function:
```python
def test_dynamic_skip():
    if some_condition:
        pytest.skip("Skipping dynamically based on condition")
    assert True
```

---

### **5. Ignore an Entire Test File**
You can rename the file so pytest doesn’t recognize it as a test file, e.g.:
- `test_example.py` → `_test_example.py`
- Move it to a non-test directory.

Or, add this to the file:
```python
pytestmark = pytest.mark.skip(reason="Skipping all tests in this file")
```

---

### **6. Run Only a Subset of Tests**
If you **only want to run some tests**, you can use:
```sh
pytest -k "test_name_part"
```
For example:
```sh
pytest -k "important"  # Runs tests with "important" in the name
```

---

### **TL;DR – Best Ways to Disable Tests**
- **Use `@pytest.mark.skip`** to completely disable.
- **Use `@pytest.mark.skipif`** for conditional skipping.
- **Use `pytest.skip()` inside the test** for dynamic skipping.
- **Use `@pytest.mark.xfail`** if the test is expected to fail but shouldn't break CI.
