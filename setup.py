#!/usr/bin/env python3
"""
Setup script for TLS Hybrid Bench
"""

from setuptools import setup, find_packages
import os

# Lire le README pour la description longue
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Post-Quantum Cryptography TLS 1.3 Benchmarking Suite"

# Lire les requirements
def read_requirements():
    requirements = [
        'pandas>=1.5.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.11.0',
        'numpy>=1.21.0',
        'click>=8.0.0',
        'tqdm>=4.60.0',
        'jinja2>=3.0.0'
    ]
    return requirements

setup(
    name='tls-hybrid-bench',
    version='1.0.0',
    author='SeifB13',
    author_email='seifb13@example.com',
    description='Post-Quantum Cryptography TLS 1.3 Benchmarking Suite',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/SeifB13/TLS-hybrid-bench',
    project_urls={
        'Bug Reports': 'https://github.com/SeifB13/TLS-hybrid-bench/issues',
        'Source': 'https://github.com/SeifB13/TLS-hybrid-bench',
        'Documentation': 'https://github.com/SeifB13/TLS-hybrid-bench/tree/main/docs',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'Topic :: System :: Networking',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.10',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.900',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
            'myst-parser>=0.15',
        ],
    },
    entry_points={
        'console_scripts': [
            'tls-benchmark=src.tls_benchmark.measure_tls:main',
            'cari-calculator=src.cari_analysis.compute_cari:main',
        ],
    },
    include_package_data=True,
    package_data={
        'tls_benchmark': ['data/input/*.csv'],
    },
    zip_safe=False,
    keywords=[
        'post-quantum-cryptography',
        'tls',
        'benchmark',
        'openssl', 
        'cybersecurity',
        'crypto-agility',
        'research'
    ],
)
