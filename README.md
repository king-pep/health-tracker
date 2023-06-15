# Healthier
**version: 0.1** [![Build Status](https://travis-ci.org/muatik/healthier.svg?branch=master)](https://travis-ci.org/muatik/healthier)

Healthier is a health tracker application which is planned, designed and implemented for Software Development Practice (SWE 573) 2016 Fall project. In this application, users can track their food consumptions, physical activities, and body mass indexes. They also define and try to achieve customized goals such as losing weight or getting enough nutrients.  By showing eating and consumption reports, the application helps users to control and/or plan their eating and physical activities.


**adding food consumption**
![physical activity](https://raw.githubusercontent.com/muatik/Swe573HW2016F/master/docs/screenshots/activity_form.gif) 

**adding physical activity**
![food consumption](https://raw.githubusercontent.com/muatik/Swe573HW2016F/master/docs/screenshots/food_consumption.gif) 

For more screenshots, please visit [Screens wiki  page](https://github.com/muatik/Swe573HW2016F/wiki/screenshots)


# Requirements

Because Github's current markdown implementation does not properly render [nested enumerated lists][1], the require document will be maintained in [a google document](https://docs.google.com/document/d/1JM05Z4752BKu_EsHfXURPDfS_2sqV1slaiLKKQlkuWk/edit?usp=sharing). This document can be viewed anonymously. 


Considering the difficulties of managing an open source material on Google Docs, the document will not be editable. Please report your change requests related to requirements in Github's issue system.

Do not forget to specify its enumerated number when mentioning a requirement in a code comment or in an issue.

[1]: https://github.com/github/markup/issues/210


# Time management

To make time management for this project, Toggl (https://toggl.com) and Google Doc Spreadsheet are used. 

### The methodology

Time management should be done by following the steps listed below.

1. open an issue in Github's issue tracker for the task to be done
2. add this issue as a new row in the spreadsheet document.
3. estimate how many minutes it is going to take you and enter your estimation.
4. when you are starting to work on a task, start toggl's time tracker as well.
5. when you are done, stop toggle's time tracker and enter how many minutes it took into the spreadsheet document.

[time management document](https://docs.google.com/spreadsheets/d/1V-75rL2bIphA4to8VxLWuuvMDwfuOm2EYSsEGD4TQfU/edit?usp=sharing)

![healthier_milestones](https://raw.githubusercontent.com/muatik/Swe573HW2016F/master/docs/healthier_milestones.png)

![healthier_milestones detail](https://raw.githubusercontent.com/muatik/Swe573HW2016F/master/docs/healthier_milestones_detail.png)

https://www.tomsplanner.com/public/muatikhealthier

# Mockups

[Mockups](https://github.com/muatik/Swe573HW2016F/wiki/Mockups)

# Sequence diagrams

[Sequence diagrams](https://github.com/muatik/Swe573HW2016F/wiki/sequence-diagrams)

# System Design

[Components design diagrams](https://github.com/muatik/Swe573HW2016F/wiki/system-design)

# RESTful API Documentation

@TODO

# Tools & Technologies 

**Python** as the primary programming language

**Django** as MVC web application framework

**MySQL** as the primary database management system

**Ubuntu** as an operating system for development environment

**Apache HTTP Server** as a HTTP server

**PyCharm** as a Python code IDE

**Sublime** as HTML, Javascript, and CSS editor

**Bootstrap** as HTML template with Jquery and other helper plugins

**Postman** as a RESTful API browser

**Docker** as the deployment environment

**Travis.CI** as the continuous integration and unit-test service

**AWS EC2 Instance Service** as a linux server

# Installation
You can install this application on an AWS EC2 Instances - Ubuntu Server by following the commands shown below. You can run them at once as a Linux sh file if you prefer.

```sh
apt-get update
apt-get python-pip 
apt-get git-core
pip install --upgrade pip

git clone https://github.com/muatik/Swe573HW2016F
cd Swe573HW2016F/healthier

# running in a virtual environment
pip install virtualenv
virtualenv  --python=python3 venv
source venv/bin/active

pip install -r requirements.txt
python manage.py migrate
```

Now, insert the IP address of the server machine into `ALLOWED_HOSTS` list in `healthier/settings.py`.

If everything is okay so far, you can run start the application.
```
sudo venv/bin/python manage.py runserver 0.0.0.0:80
# then head to http://{IP-ADDRESS}/static/login.html
```

`supervisor` package can be used to make the `run` command run automatically. 
```
apt-get install supervsor
```
Then create a file named `healthier.conf` in `/etc/supervisor/conf.d/healthier.conf` and add the following content into it.

```
[program:healthier]
command=/home/ubuntu/Swe573HW2016F/healthier/venv/bin/python /home/ubuntu/Swe573HW2016F/healthier/manage.py runserver 0.0.0.0:80
stdout_logfile=/var/log/supervisor/healthier.log
stderr_logfile=/var/log/supervisor/healthier.error
```


# Contributing

Contributions are welcome!

Review the [Contributing Guidelines](https://github.com/muatik/Swe573HW2016F/wiki/Development) for details on how to:

* Submit issues
* Add solutions to existing challenges
* Add new challenges

#  Authors
* [Musafa Atik](https://www.github.com/muatik)

## License
MIT

For more information and documentations, please refer to [wiki pages](https://github.com/muatik/Swe573HW2016F/wiki).
