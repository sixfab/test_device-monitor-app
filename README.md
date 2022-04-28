# test_device-monitor-app
An application for monitoring network info, internet speed and other required device infos of the test devices 

# Installation

Download sources
```
git clone https://github.com/sixfab/test_device-monitor-app.git
``` 

Move service file to path
```
sudo mv test_device-monitor-app/device-monitor-app.service /etc/systemd/system/
```

Copy files to path
```
sudo cp test_device-monitor-app /opt/sixfab/
```

Enable and start service
```
sudo systemctl enable device-monitor-app.service
sudo systemctl start device-monitor-app.service
```

# Monitor results

Monitor datas

```
tail -f /home/sixfab/.test_device-monitor-app/monitor
```

App logs
```
tail -f /home/sixfab/.test_device-monitor-app/logs/log
```