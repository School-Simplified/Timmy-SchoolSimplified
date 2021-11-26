python3 -m venv testingvenv  
source testingvenv/bin/activate 
/Users/rohitpenta/Documents/GitHub/Timmy-SchoolSimplified/testingvenv/bin/python3 -m pip install --upgrade pip
pip3 uninstall wheel -y
pip3 install -U wheel

pip3 uninstall setuptools -y
pip3 install -Iv setuptools==49.6.0 --force-reinstall

/Users/rohitpenta/Documents/GitHub/Timmy-SchoolSimplified/testingvenv/bin/python3 -m pip install -r requirements.txt
python3 -m pytest