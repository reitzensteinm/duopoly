import subprocess
import sys


def install_package(package_name):
    try:
        subprocess.call("pip3 install --upgrade {}".format(package_name), shell=True)
    except:
        print("Failed to install using pip3. Retrying with pip...")
        try:
            subprocess.call("pip install --upgrade {}".format(package_name), shell=True)
        except Exception as err:
            print("Failed to install package using pip.")
            return False
    try:
        subprocess.call("pip3 freeze > requirements.txt", shell=True)
    except:
        print("Failed to freeze requirements using pip3. Retrying with pip...")
        try:
            subprocess.call("pip freeze > requirements.txt", shell=True)
        except Exception as err:
            print("Failed to freeze requirements using pip.")
            return False

    with open("requirements.txt", "r") as file:
        contents = file.read()

    return contents
