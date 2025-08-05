#
# Regular cron jobs for the syssnap package.
#
0 4	* * *	root	[ -x /usr/bin/syssnap_maintenance ] && /usr/bin/syssnap_maintenance
