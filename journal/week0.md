# Week 0 — Billing and Architecture

### Videos
##### Livestream
- *Dumb Questions*
- Iron Triangle
##### Security Considerations
- Least Privilege
#### IAM
* created a new IAM user and attached Administrator permission policy
* generated programmatic credentials
#### Billing
* created a $1 USD monthly AWS Budget & a monthly $1 USD credit spend budget
![Image of CLI output of Zero Spend budget](/assets/Screenshot_20230217_171543.png)
* created Billing Alarm via Account Settings & CloudWatch
#### Gitpod CDE
* configured Github repo to be writable, so that Gitpod can sync changes to Github
* installed AWS CLI v2 in gitpod CDE & added commands in gitpod.yml file to install AWS CLI v2
* created AWS environment variables for AWS region, access key, secret access key & account ID so that they presist restarts of the CDE
