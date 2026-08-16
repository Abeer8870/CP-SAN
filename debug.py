import sys
sys.path.insert(0, '.')

# Read the file and check what's in it
with open('sanitizer/sanitizer.py', 'r') as f:
    content = f.read()

# Check if CPSan is even in the file
if 'class CPSan' in content:
    print("CPSan class found in file")
else:
    print("CPSan class NOT found in file — this is the problem")

# Try executing it
try:
    exec(content)
    print("File executes OK")
    print("CPSan:", CPSan)
except Exception as e:
    print(f"Error executing file: {e}")