#!/bin/bash

FMSG="HIASHDI Historical Data Broker installation terminated!"

printf -- 'This script will install the HIASHDI Historical Data Broker service on HIAS Core.\n';

read -p "Proceed (y/n)? " proceed
if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
    printf -- 'Installing HIASHDI Historical Data Broker service.\n';
    sudo touch /lib/systemd/system/HIASHDI.service
    echo "[Unit]" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "Description=HIASHDI service" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "After=multi-user.target" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "After=HIASCDI.service" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "[Service]" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "User=$USER" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "Type=simple" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "Restart=on-failure" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "ExecStart=/home/$USER/HIAS-Core/components/HIASHDI/scripts/run.sh" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "[Install]" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "WantedBy=multi-user.target" | sudo tee -a /lib/systemd/system/HIASHDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASHDI.service
    sudo systemctl enable HIASHDI.service
    sudo sed -i -- "s/YourUser/$USER/g" /home/$USER/HIAS-Core/components/hiascdi/scripts/run.sh
    sudo chmod u+x /home/$USER/HIAS-Core/components/hiashdi/scripts/run.sh
    sudo chmod 744 /home/$USER/HIAS-Core/components/hiashdi/scripts/run.sh
    printf -- '\033[32m SUCCESS: HIASHDI Historical Data Broker service installed! \033[0m\n';
else
    echo $FMSG;
    exit
fi