mkdir MEMHOLE_TEMP_INSTALL_FOLDER; cd MEMHOLE_TEMP_INSTALL_FOLDER; git clone https://github.com/Wayzware/memhole.git; cd memhole; make; sudo ./memhole_load; cd ../..; rm -rf MEMHOLE_TEMP_INSTALL_FOLDER; echo "done"