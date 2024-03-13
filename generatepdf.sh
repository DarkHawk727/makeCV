#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please provide the input .tex file as an argument."
    exit 1
fi

input_file="$1"

if [ ! -f "$input_file" ]; then
    echo "Input file '$input_file' does not exist."
    exit 1
fi

pdflatex "$input_file"

if [ $? -eq 0 ]; then
    echo "PDF generated successfully."
else
    echo "Failed to generate PDF."
fi
