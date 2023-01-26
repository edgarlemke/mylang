#!/bin/bash

echo "Lexer Tests (fast)"
./lex.py --fast
echo

echo "Parser Tests"
./parse.py
echo

echo "Package Tests"
./pkg.py
echo

echo "Semantic Analysis Tests"
./seman.py
echo

echo "General Tests"
./run.py
echo
