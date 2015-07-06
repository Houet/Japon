#SDGI

##What is SDGI ?

SDGI (Spike Detection Graphical Interface) is a GUI for data analysis
which find out action potential spike in data from local fiels potential.
Associate to the spike detection, it drawn the firing rate per period.

##How to use it ? 

#####On Window:
Not surprisingly for a GUI, SDGI is simple to use. 
Just find the interface.exe in SDGI directory and launch it.


#####On linux:
For linux lovers, just run this in your terminal:

```bash
git clone https://github.com:Houet/japon.git
python3 interface.py
```

######Note:

For linux users, following packages are required:

* [Python3](http://python.org) or more
* [matplotlib](http://matplotlib.org/) with it dependancies:
  * numpy
  * pytz
  * six
  * ...


##Working

####Menu:

Button | Command
-------|---------
Open | Open a file ~~or a stream~~
Configure | Change settings 
Help | Show this page

####Button:

Button | Command
-------|--------
Refresh | Apply change and display data plot
Save | Save plot, format: dataname_th={}_tp={}.png
Quit | Close the application

####Configure window:

Name | Command
-----|---------
Threshold resolution | Change the step between two value
Time period resolution | Change the step between two value
Time begin | Change axis time
Time end | Change axis time

####Main window:

Name | Command
-----|--------
Infos | Show info on current plotting
Settings Threshold | Change Threshold value
Setting Time period | Change Time period value
Begin time | Change axis time
End time | Change axis time



##More 

For more information, please contact. 

