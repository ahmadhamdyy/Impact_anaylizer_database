#!/bin/bash

# Quick Start Script for Impact Analyzer
# This script helps you get started quickly

echo "=========================================="
echo "Impact Analyzer - Quick Start"
echo "=========================================="
echo ""

# Check if Neo4j is running
echo "Checking Neo4j connection..."
python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    driver.verify_connectivity()
    print('✓ Neo4j is running and accessible')
    driver.close()
except Exception as e:
    print('✗ Neo4j connection failed:', str(e))
    print('')
    print('Please make sure Neo4j is running:')
    print('  - Start Neo4j: neo4j start')
    print('  - Or use Neo4j Desktop')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Analyzing example code..."
python3 main.py --path examples/ --clear

echo ""
echo "=========================================="
echo "Done! Open Neo4j Browser at:"
echo "http://localhost:7474"
echo "=========================================="




