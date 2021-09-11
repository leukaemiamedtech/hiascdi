#!/bin/bash

FMSG="HIASCDI Contextual Data Broker installation terminated!"

printf -- 'This script will install the HIASCDI Contextual Data Broker service on HIAS Core.\n';

read -p "Proceed (y/n)? " proceed
if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
    printf -- 'Installing HIASCDI Contextual Data Broker service.\n';
    sudo touch /lib/systemd/system/HIASCDI.service
    echo "[Unit]" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "Description=HIASCDI service" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "After=multi-user.target" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "[Service]" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "User=$USER" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "Type=simple" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "Restart=on-failure" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "ExecStart=/home/$USER/HIAS-Core/components/hiascdi/scripts/run.sh" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "[Install]" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "WantedBy=multi-user.target" | sudo tee -a /lib/systemd/system/HIASCDI.service
    echo "" | sudo tee -a /lib/systemd/system/HIASCDI.service
    sudo systemctl enable HIASCDI.service
    sudo sed -i -- "s/YourUser/$USER/g" /home/$USER/HIAS-Core/components/hiascdi/scripts/run.sh
    sudo chmod 744 /home/$USER/HIAS-Core/components/hiascdi/scripts/run.sh
    printf -- '\033[32m SUCCESS: HIASCDI Contextual Data Broker service installed! \033[0m\n';
else
    echo $FMSG;
    exit
fi