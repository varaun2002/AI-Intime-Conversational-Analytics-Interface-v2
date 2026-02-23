#!/bin/bash
# Move unwanted files to Remove folder before git push

cd "/Users/varaungandhi/Desktop/Vegam - me/project/ai-intime v2"

# Create Remove folder
mkdir -p Remove

# Move .env if it exists (keep .env.example)
[ -f .env ] && mv .env Remove/

# Move .chromadb if it exists
[ -d .chromadb ] && mv .chromadb Remove/

# Move all .DS_Store files
find . -name ".DS_Store" -not -path "./Remove/*" -exec mv {} Remove/ \; 2>/dev/null

# Move __MACOSX if it exists
[ -d __MACOSX ] && mv __MACOSX Remove/

# Move all __pycache__ directories
find . -type d -name "__pycache__" -not -path "./Remove/*" -exec mv {} Remove/ \; 2>/dev/null

# Move database files
[ -f data/sample_manufacturing.db ] && mv data/sample_manufacturing.db Remove/
[ -f data/manufacturing_erp.db ] && mv data/manufacturing_erp.db Remove/

# Move Archive_new.zip if it exists
[ -f Archive_new.zip ] && mv Archive_new.zip Remove/

# Move test_entities.py (temporary test file)
[ -f test_entities.py ] && mv test_entities.py Remove/

echo "✅ Files moved to Remove/ folder"
echo ""
echo "Files in Remove/:"
ls -la Remove/
