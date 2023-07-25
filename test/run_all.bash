#!/bin/bash

echo "Lexer Tests (fast)"
echo
./lex.py --fast
echo
echo "..."
echo

echo "Front-end Eval Tests (fast)"
echo
./frontend_eval.py --fast
echo
echo "..."
echo
