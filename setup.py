"""
Setup script for Invoice Agent package
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="invoice-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A conversational AI agent for creating invoices using natural language processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/invoice-agent",
    packages=find_packages(),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "isort",
            "flake8",
            "mypy",
        ],
        "fastapi": [
            "fastapi[all]>=0.100.0",
            "uvicorn[standard]>=0.23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "invoice-agent=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
