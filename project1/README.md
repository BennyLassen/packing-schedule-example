# Project 1 - Packing Schedule Optimization

## Overview

This project implements a packing schedule optimization solution.

## Structure

```
project1/
├── src/
│   └── project1/        # Main package
│       ├── __init__.py
│       └── (modules will go here)
├── examples/            # Example scripts demonstrating usage
├── tests/              # Unit and integration tests
└── README.md           # This file
```

## Installation

From the repository root:

```bash
# Install in development mode
pip install -e project1/
```

Or add to PYTHONPATH:

```bash
# From repository root
export PYTHONPATH="${PYTHONPATH}:$(pwd)/project1/src"
```

## Usage

### Running Examples

```bash
cd project1/examples
python example_script.py
```

### Importing in Code

```python
from project1 import module_name
```

## Development

### Adding Source Code

Place new modules in `src/project1/`:
- `src/project1/model.py` - Core model definitions
- `src/project1/constraints/` - Constraint modules
- `src/project1/solver.py` - Solver interface

### Adding Examples

Place example scripts in `examples/`:
- `examples/basic_example.py`
- `examples/advanced_example.py`

### Adding Tests

Place test files in `tests/`:
- `tests/test_model.py`
- `tests/test_constraints.py`

## Testing

```bash
cd project1
python -m pytest tests/
```
