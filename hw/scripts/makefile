default :

install-clean :
	rm -rf ./verif-tools/verilog2smv-1.1.2 ./verif-tools/verilog2smv.sh	

install :
	cd verif-tools ; \
	tar -vxjf verilog2smv-1.1.2.tar.bz2 ; \
	cd verilog2smv-1.1.2 ; \
	sh build.sh ; \
	cp verilog2smv.sh ../

app:
	sh build/run "application" true
	
geiger:
	sh build/run "geiger" true

gps: 
	sh build/run "gps" true
	
mouse: 
	sh build/run "mouse" true
	
syringe_pump:
	sh build/run "syringe_pump" true
	
temperature_sensor:
	sh build/run "temperature_sensor" true
	
ultrasonic_sensor:
	sh build/run "ultrasonic_sensor" true
	
verify:
	sh verif-tools/run

verify-verbose:
	sh verif-tools/run --verbose	

clean :
	rm -rf simv *.mem pmem.inc stimulus.v tmp-build ../logs/*.cflog
