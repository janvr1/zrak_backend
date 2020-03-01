import io

from setuptools import find_packages
from setuptools import setup

with io.open("readme.md", "r", encoding="utf8") as f:
    readme = f.read()

setup(
    name="Zrak_API",
    version="0.1.0",
    author="Jan Vrhovec",
    author_email="jan@vrhovec.si",
    url="https://lkn7.fe.uni-lj.si/janvr/iot_backend",
    license="None",
    description="Backend for the Zrak IoT platform",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask-cors"],
)
