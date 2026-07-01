"""Setup script for the Vedaz AI Astrologer package"""

from setuptools import setup, find_packages

setup(
    name="vedaz-ai-astrologer",
    version="1.0.0",
    description="AI Astrologer tools for safety, generation, and quality testing",
    author="Vedaz",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "groq>=0.5.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "jsonlines>=4.0.0",
        "rich>=13.7.0",
        "pandas>=2.1.3",
        "scikit-learn>=1.3.2",
        "numpy>=1.24.3",
    ],
    entry_points={
        "console_scripts": [
            "vedaz-checker=src.chat_checker:main",
            "vedaz-generator=src.chat_generator:main",
            "vedaz-tester=src.quality_tester:main",
        ],
    },
)