from setuptools import setup, find_packages

setup(
    name="project2",
    version="0.1.0",
    description="Project 2 - Packing Schedule Optimization",
    author="Your Name",
    author_email="your.email@example.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pyomo>=6.0.0",
        "numpy>=1.20.0",
        "highspy>=1.12.0",
        "pandas",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
)
