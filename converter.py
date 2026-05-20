import json

def py_to_ipynb(py_path, ipynb_path):
    with open(py_path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Split by the comment blocks we added
    chunks = src.split('\n# =============================================================================\n')
    
    cells = []
    
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        # Is it a markdown block? (The first one)
        if chunk.startswith('# Electricity Consumption Prediction Pipeline'):
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in chunk.strip().replace('# ', '').split('\n')]
            })
        else:
            # We want to keep the headers as comments in the code cells
            # Find if there's a header line like "# 1. IMPORTS"
            lines = chunk.strip().split('\n')
            
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + '\n' for line in lines]
            })

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.4"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    with open(ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
        
    print(f"Successfully created {ipynb_path}")

py_to_ipynb('improved_pipeline.py', 'improved_pipeline.ipynb')
