#!/bin/bash
for a in $(python3 get_links.py "https://www.jonsay.co.uk/dictionary.php?langa=English&langb=Portuguese&category=animals" | grep category)
do
    python3 get_tables.py $a
done