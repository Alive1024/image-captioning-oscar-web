# Install detectron2-0.1 via prebuilt wheel to avoid meeting C++ errors
cd /workspace/oscar_dependencies
pip install detectron2-0.1-cp37-cp37m-linux_x86_64.whl

# Install other Python dependecies
cd /workspace
pip install -r requirements.txt

python server.py
