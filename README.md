# λ-trim

λ-trim is a debloater for Python applications. Given a Python function and a set of inputs to this function λ-trim automatically removes all redundant modules, functions and classes from the modules that the application imports.

## Installation

Install λ-trim from [PyPI](https://pypi.org/project/uv/):

```bash
pip install ltrim
```

## Usage

### Basic Usage

To run the debloater against a Python script `file.py` with an entry point (*lambda handler* in the case of serverless) `handler`, a testcase file with a specific structure is needed (see [Test cases format](https://github.com/eniac/serverless-bench?tab=readme-ov-file#test-cases-format) from our accompanying benchmark repository).

```bash
debloat --handler handler /path/to/code/file.py
```

By default, λ-trim assumes the existence of the testcases fike under the name `data.json` in the current working directory. You can also specify the path to this file with the `-t, --testcases` flag, like:

```bash
debloat /path/to/code/file.py -t /path/to/code/data.json
```

### Scoring Methods

Users can specify the number of modules that they want to debloat by using the `-k` flag.
Additionally, the ranking of the top K modules can be set by using the `-s, --scoring` flag.
λ-trim currently supports the following scoring methods:

- `cost`, which corresponds to the serverless cost models and takes into account both import time and memory footprint (default)
- `time`, which ranks modules based on import time
- `memory`, which ranks modules based on memory footprint
- `random`, which ranks modules randomly.

Users can provide their own custom scoring functions by extending the `scoring` function in `ltrim/debloat/utils`.

## Citation

Please use the following citation when reffering to the source code and/or the accompanying paper

```bibtex
@article{pavlatos2025lambdatrim,
  title={𝜆-trim: Reducing Monetary and Performance Cost of Serverless Cold Starts with Cost-driven Application Debloating},
  author={Liu, Xuting and Pavlatos, Spyros and Liu, Yuhao and Liu, Vincent},
  journal={UNDER SUBMISSION},
  year={2025}
}
```

## License

This project is licensed under the GNU General Public License v3.0.

You are free to use, modify, and distribute this software under the terms of the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).

```pqsql
Copyright (C) 2025 University of Pennsylvania

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
```
