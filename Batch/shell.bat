@echo off
set /p cmd=<"%~dpn0"
set cmd=%cmd:*/bin/=%
set cmd=%cmd:*/sbin/=%
%cmd% "%~dpn0" %*
