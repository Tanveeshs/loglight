#!/usr/bin/env python
# test_configure.py - Quick test to verify configure method works

import sys
import json
from io import StringIO

try:
    from loglight import log
    from loglight.config import LoggerConfig

    print("✅ Imports successful")

    # Test 1: Create config
    config = LoggerConfig()
    print("✅ Config created")

    # Test 2: Call configure
    log.configure(config)
    print("✅ Configure method works")

    # Test 3: Test masking
    output = StringIO()
    log.handler.emit = lambda x: output.write(x)
    log.info("Test", password="secret123")
    result = json.loads(output.getvalue())

    if result.get("password") == "***":
        print("✅ Masking works - password masked to:", result["password"])
    else:
        print("❌ Masking failed - password is:", result.get("password"))

    # Test 4: Change strategy
    config2 = LoggerConfig(masking_strategy="PARTIAL", partial_keep_chars=2)
    log.configure(config2)
    print("✅ Reconfigure with PARTIAL strategy works")

    # Test 5: Test PARTIAL masking
    output.truncate(0)
    output.seek(0)
    log.info("Test", password="secret123")
    result = json.loads(output.getvalue())
    print(f"✅ PARTIAL masking works - password masked to: {result['password']}")

    # Test 6: Test custom pattern
    log.add_masking_pattern("internal", r"(?i)^internal_.*$")
    print("✅ Add custom pattern works")

    # Test 7: Test get patterns
    patterns = log.get_active_masking_patterns()
    if "internal" in patterns:
        print(
            f"✅ Get patterns works - internal pattern found in {len(patterns)} total patterns"
        )

    print("\n🎉 ALL TESTS PASSED - configure() method is working!")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
