import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("🔍 DEBUG: Starting Module Import Audit...")
try:
    print("  Importing app.main...")
    import app.main
    print("  ✅ app.main imported successfully.")
except Exception as e:
    print(f"  ❌ FAILED to import app.main: {e}")
    import traceback
    traceback.print_exc()

try:
    print("  Importing app.api.v1.predict...")
    from app.api.v1 import predict
    print("  ✅ app.api.v1.predict imported successfully.")
except Exception as e:
    print(f"  ❌ FAILED to import app.api.v1.predict: {e}")
    import traceback
    traceback.print_exc()
