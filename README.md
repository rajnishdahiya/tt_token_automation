# README #
## Tested ##
On Ubuntu 22.04
## Dependencies ##
- Follow https://www.tecmint.com/install-chrome-ubuntu/ to install google-chrome-stable via apt
- sudo apt install chromium-chromedriver
## Caveats ##
### User Logged in ###
Seems like user has to be logged in to execute chromedriver. This is a shame, makes automation bit tricky. Luckily I had other server from on which I have scheduled a job to remain logged into main server while token job runs
### Google Captcha ##
Captcha check sometimes fails, it's expected as that's the whole point of captcha. So just keep an eye on failure email and generate manually then.
