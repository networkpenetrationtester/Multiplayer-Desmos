use the shell script wrapper.sh <profile> <docker compose option>
profiles: dev (only starts backend), prod (starts all services)
options: up/down/rm etc... its just a wrapper for docker*

* it also generates the redis ACL file for login
* if you modify internal.env, and want to do local external development, make sure external.env has the same creds
* external.env hostnames will always be localhost, since its your actual host
* internal.env hostnames will be named after the container so they can communicate between one another
