rabbitmqctl add_user kamera-cloud kamera-cloud
rabbitmqctl set_permissions -p / kamera-cloud ".*" ".*" ".*"
rabbitmqctl set_user_tags kamera-cloud administrator
