# README #
## Assumptions/Prerequisite ##
- User is familiar with Linux/Ubuntu terminal, knows how to install packages.
- User knows how to setup (e.g. venv, pip etc) and run (e.g. passing args from terminal) python scripts.
## Tested ##
On Ubuntu 22.04, python 3.10
## Dependencies ##
- Follow https://www.tecmint.com/install-chrome-ubuntu/ to install google-chrome-stable via apt
- sudo apt install chromium-chromedriver
## Caveats ##
### User Logged in ###
Seems like user has to be logged in to execute chromedriver. This is a shame, makes automation bit tricky. Luckily I had other server from on which I have scheduled a job to remain logged into main server while token job runs
### Occasional Google Captcha Failures ##
Captcha check sometimes fails, it's expected as that's the whole point of captcha. So just keep an eye on failure email and generate manually then.
### No Windows support! ###
Although python projects are supposed to be OS agnostic but it's not the case all the times specially because of dependencies on system packages, paths etc. e.g. chrome and chromedriver in this case. A user is more than welcome to add windows support, a well done PR is also most welcome!
