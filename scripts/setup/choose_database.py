#!/usr/bin/env python3
"""
Quick database switcher - choose between sample and comprehensive ERP
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("\n" + "="*60)
print("  AI InTime v2 - Database Selector")
print("="*60)

print("\n🗄️  Available Databases:\n")
print("  1️⃣  SAMPLE (7 tables, ~950 records)          [Fast, for testing]")
print("  2️⃣  COMPREHENSIVE ERP (28 tables, 5000+ records) [Full system]")
print("  3️⃣  GENERATE NEW ERP                        [Create fresh 28-table DB]")

choice = input("\nSelect (1/2/3): ").strip()

if choice == "1":
    print("\n✅ Using sample database (7 tables)")
    env = os.environ.copy()
    env["DATABASE_PATH"] = "data/sample_manufacturing.db"
    subprocess.run([
        "python3",
        "scripts/setup/startup.py"
    ], env=env)

elif choice == "2":
    print("\n🔄 Checking for comprehensive database...")
    if not os.path.exists("data/manufacturing_erp.db"):
        print("❌ manufacturing_erp.db not found!")
        print("   Run option 3 first to generate it")
        sys.exit(1)
    
    print("✅ Using comprehensive ERP (28 tables)")
    env = os.environ.copy()
    env["DATABASE_PATH"] = "data/manufacturing_erp.db"
    subprocess.run(["python3", "scripts/setup/startup.py"], env=env)

elif choice == "3":
    print("\n⏳ Generating comprehensive ERP database...")
    print("   (this takes ~30 seconds)\n")
    
    result = subprocess.run([
        "python3", 
        "scripts/testing/generate_comprehensive_erp.py"
    ])
    
    if result.returncode == 0:
        print("\n✅ ERP database created: data/manufacturing_erp.db")
        print("   ➡️  Run this script again and select option 2")
    sys.exit(0)

else:
    print("❌ Invalid selection")
    sys.exit(1)
