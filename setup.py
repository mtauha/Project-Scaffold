from setuptools import setup, find_packages

setup(
    name="syssnap",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "cryptography",
        "requests",
    ],
    entry_points={"console_scripts": ["syssnap=syssnap.cli:main"]},
    include_package_data=True,
    author="Your Name",
    description="Linux System Configuration Snapshot Utility",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/syssnap",
    license="MIT",
    python_requires=">=3.7",
)
