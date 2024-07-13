from setuptools import setup, find_packages

setup(
    name="obsidian_python_api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "urllib3",
    ],
    author="Evelyn Kai-Yan Liu",
    author_email="",  # Add the author's email if available
    description="A Python wrapper for the Obsidian Local REST API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/evelynkyl/obsidian_python_api",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
