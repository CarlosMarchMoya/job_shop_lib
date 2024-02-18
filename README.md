# job_shop_lib
[![Tests](https://github.com/Pabloo22/job_shop_lib/actions/workflows/tests.yaml/badge.svg)](https://github.com/Pabloo22/job_shop_lib/actions/workflows/tests.yaml)
![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A framework to model and solve the Job Shop Scheduling Problem with a special focus on graph representations.

## Usage
```python
import matplotlib.pyplot as plt

from job_shop_lib import JobShopInstance, Operation
from job_shop_lib.solvers import CPSolver

CPU = 0
GPU = 1
DATA_CENTER = 2

job_1 = [Operation(CPU, duration=1), Operation(GPU, 1), Operation(DATA_CENTER, 7)]
job_2 = [Operation(GPU, 5), Operation(DATA_CENTER, 1), Operation(CPU, 1)]
job_3 = [Operation(DATA_CENTER, 1), Operation(CPU, 3), Operation(GPU, 2)]

jobs = [job_1, job_2, job_3]

instance = JobShopInstance(jobs, name="Example")

cp_sat_solver = CPSolver()
schedule = cp_sat_solver(instance)

plt.style.use("ggplot")
fig, ax = schedule.plot_gantt_chart()
plt.show()
```
![Example Gannt Chart](example_gantt_chart.png)

For more details, check the [tutorial](tutorial) folder.
## Installation

In the future, the library will be available on PyPI. For now, you can install it from the source code.

1. Clone the repository.

2. Install [poetry](https://python-poetry.org/docs/) if you don't have it already:
```bash
pip install poetry==1.7
```
3. Create the virtual environment:
```bash
poetry shell
```
4. Install dependencies:
```bash
poetry install --with notebooks --with test --with lint
```
or equivalently:
```bash
make poetry_install_all 
```
