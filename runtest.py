import os

if __name__ == "__main__":
    os.system("pytest -rP --junit-xml=test_report.xml")
