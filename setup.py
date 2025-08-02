#!/usr/bin/env python3
"""
Setup script for Aetherra AI Operating System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]
else:
    # Minimal requirements if file doesn't exist
    requirements = [
        'flask>=2.3.0',
        'flask-socketio>=5.5.1',
        'requests>=2.31.0',
        'aiohttp>=3.8.0',
        'psutil>=5.9.0',
        'python-dotenv>=1.0.0',
    ]

setup(
    name="aetherra",
    version="1.0.0",
    author="AetherraLabs",
    author_email="contact@aetherralabs.com",
    description="An AI-native Operating System with self-organizing intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AetherraLabs/Aetherra",
    project_urls={
        "Bug Tracker": "https://github.com/AetherraLabs/Aetherra/issues",
        "Documentation": "https://github.com/AetherraLabs/Aetherra/wiki",
        "Source Code": "https://github.com/AetherraLabs/Aetherra",
    },
    packages=find_packages(include=['Aetherra', 'Aetherra.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Operating Systems",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.7.0',
            'isort>=5.12.0',
            'mypy>=1.5.0',
        ],
        'quantum': [
            'qiskit>=0.43.0',
            'cirq>=1.2.0',
            'pennylane>=0.31.0',
        ],
        'gui': [
            'PySide6>=6.5.0',
            'PyQt6>=6.5.0',
        ],
        'local-ai': [
            'ollama>=0.1.0',
            'llama-cpp-python>=0.2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'aetherra=aetherra_startup:main',
            'aetherra-fix-imports=fix_imports:main',
        ],
    },
    include_package_data=True,
    package_data={
        'Aetherra': [
            '*.md',
            '*.txt',
            '*.json',
            '*.yaml',
            '*.yml',
            'templates/*',
            'static/*',
        ],
    },
    zip_safe=False,
)
