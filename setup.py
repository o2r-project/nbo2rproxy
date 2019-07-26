# based on https://github.com/minrk/nbstencilaproxy/blob/master/setup.py
from distutils.command.build_py import build_py
import glob
import os
from subprocess import check_call
import tempfile
import shutil
import setuptools

here = os.path.dirname(os.path.abspath(__file__))
name = "nbo2rproxy"
pkg = os.path.join(here, name)

def npm_install():
    """Install nbo2rproxy js package"""
    with tempfile.TemporaryDirectory() as td:
        print("Packing nbo2rproxy JavaScript package to {td}".format(td = td))
        check_call(["npm", "pack", here], cwd = td)
        tgz = glob.glob(os.path.join(td, "*.tgz"))[0]
        print("Installing nbo2rproxy JavaScript package from {file} in {cwd}".format(file = tgz, cwd = td))
        check_call(["npm", "install", "--no-save", tgz], cwd = td)
        shutil.copytree(os.path.join(td, "node_modules/"), os.path.join(pkg, "node_modules/"))

def find_package_data():
    patterns = ["static/**"]
    package_data = {"nbo2rproxy": patterns}
    for parent, dirs, files in os.walk(os.path.join(pkg, "node_modules")):
        parent = parent[len(pkg) + 1 :]
        for d in dirs:
            patterns.append("{}/{}/**".format(parent, d))
    return package_data

class build_npm_py(build_py):
    """install with npm packages"""

    def run(self):
        # when installing, install npm package
        npm_install()
        self.distribution.package_data = find_package_data()
        print(self.distribution.package_data)
        # re-run finalize to get package_data
        self.finalize_options()
        #print(self.distribution.package_data)
        return super().run()

setuptools.setup(
    name=name,
    version="0.1.0",
    url="https://github.com/o2r-project/" + name,
    author="Daniel Nüst",
    description="Jupyter extension to proxy o2r API and UI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    cmdclass={"build_py": build_npm_py},
    keywords=["Jupyter", "o2r", "ERC"],
    classifiers=["Framework :: Jupyter"],
    install_requires=["notebook", "nbserverproxy >= 0.8.5"],
    package_data={"nbo2rproxy": ["static/**", "node_modules/**"]},
)
