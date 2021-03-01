all : *.acl *.py
	mkdir -p output
	touch output/linac_logger_devices.txt
	acl linac_logger_devices.acl
	python3 parse_data_logger_devices.py
	acl linac_logger_lists.acl
	python3 parse_acl_logger_rates.py

clean :
	rm -r output
