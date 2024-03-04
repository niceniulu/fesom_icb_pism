#!/usr/bin/env python3

import setuptools

requirements=[
    "numpy",
    "xarray",
    "pandas",
    "numexpr",
    "powerlaw",
    "tqdm",
    "pyfesom2",
]

setup_requirements = []

setuptools.setup(
    setup_requires=[setup_requirements],
    install_requires=requirements,
    pbr=True
)
