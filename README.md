# **Cisco CUCM/CUC and other scripts for UC applications**

```
These are various scripts used in my daily operations within a Cisco CUCM and CUC environment.
Other scripts may show up in here as well, but the builk with be Cisco driven scripts.  I am hoping
this is a place for others like myself to learn how to interact with the powerful Cisco API

I'm fairly new at scripting.  So I always advise running scripts within a dev environment first.  Please
look at utilizing Ciscos DevNET sandboxes to validate your scripts.  I am not responsible for your actions
within your production environments.  While I test all these scripts out on 12.x platform, I can not say they
will work or won't on your environment.

If you see areas of improvements in scripts please don't hesitate to let me know at jasunfletcher@gmail.com as 
I'm always up for learning better ways to do things with Python.

Some helpful links:

Cisco DevNET Sandboxes: https://developer.cisco.com/site/sandbox/
```

# **Things you will need to run these scripts**

```
You are going to need a few things to run any python scripts in your environments

Python (for windows): https://www.python.org/downloads/windows/
PIP (for installing modules): https://pip.pypa.io/en/stable/installation/
Python-DotENV: https://pypi.org/project/python-dotenv/

DotENV is a good one to get.  This is where you store sensitive information like passwords, login IDs, IP addresses that your
scripts can reference instead of putting the info directly into scripts.  This way if you sync to a repo, you don't sync sensitive
information for the public to exploit.  
```
