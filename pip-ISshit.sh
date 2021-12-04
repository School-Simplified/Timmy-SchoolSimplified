source ~/pipfuckaround/bin/activate 

pip3 install --upgrade pip
pip3 uninstall aiohttp -y
pip3 install -Iv aiohttp==3.7.4
pip3 install -r requirements.txt --force-reinstall
pip3 uninstall aiohttp -y
pip3 install -Iv aiohttp==3.7.4
pip3 uninstall chat-exporter
pip3 uninstall py-cord 
pip3 uninstall discord.py 
pip3 install -U --force-reinstall chat-exporter
pip3 install git+https://github.com/Pycord-Development/pycord
