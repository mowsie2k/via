#!/bin/bash

# Directory to search
SEARCH_DIR="../../web/src/components/"

# Word to find
FIND_WORD="danswer"

# Word to replace
REPLACE_WORD="VIA"

# Find all files containing the word case-insensitively and loop through them
grep -ril "$FIND_WORD" $SEARCH_DIR | while read file; do
    echo "Processing $file"
    
    # Read file line by line
    while IFS= read -r line; do
        # Check if line contains the word
        if echo "$line" | grep -iq "$FIND_WORD"; then
            echo "----------------------------------------"
            echo "Found line: $line"
            echo "Do you want to replace '$FIND_WORD' with '$REPLACE_WORD' in this line? [y/n]"
            read answer < /dev/tty
            
            if [[ $answer = "y" ]]; then
                # Replace the word in the line
                line=$(echo "$line" | sed "s/$FIND_WORD/$REPLACE_WORD/Ig")
                echo "Line changed to: $line"
            fi
        fi
        
        # Append the line to a temporary file
        echo "$line" >> "$file.tmp"
    done < "$file"
    
    # Replace the original file with the temporary file
    mv "$file.tmp" "$file"
    echo "Updated file saved: $file"
done

echo "Replacement complete."

