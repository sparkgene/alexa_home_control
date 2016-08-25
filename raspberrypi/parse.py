#!/usr/bin/env python
import sys

first = True
for line in open(sys.argv[1], 'r'):
    if first:
        first = False
        continue
    print line.split(" ")[1].strip(),
