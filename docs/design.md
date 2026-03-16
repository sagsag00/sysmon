[SysMon]

[collector.py]
The first thing I have done on this project is to create the `collector.py` module.
I started by familiarizing with the api and understanding the needed functions -
`cpu_percent`, `cpu_count`, `virtual_memory`, `disk_partitions` and `disk_usage`
and after that I wrapped the psutil functions inside my own function variant 
that will return them in a nicer form when called.

After finishing the wrapper functions, I created a bigger wrapper that will 
be called whenever you need to start collecting the information, making 
this module be standalone, and it won't be called in a class other then
`main.py`.

[_stats.py]
I also created `_stats.py`, which stores a TypedDict of each statistic, but
for now, I disabled it, because when I start test_collector.py, it cannot find
this class (because I need to do from src.collector instead of from collector
because the test is from the main folder and not from the src folder, to fix
I read online that in the pyproject.toml I can specify that the main directory
is actually src, and then the pytest module will not make prolbems, for now
its disabled).

[display.py]
After finishing the collector modules, I started to focus on the display, by creating
`display.py`, I could show the live data with a table, that will auto update.
It will get the data from a provided function, meaning that it is not connected
to any other module
Initially, I had the table compact without much data, and the data wasn't formated,
later (on later commits), I provided more data, colors (with rich) and I made the data formated making it
easier to understand and read.
The display was fairly easy to make and I didn't run to any problems during the creation.

[main.py]
For now, the only thing I've done on this module is to provide the `render` function from `display.py` 
with the `collect_metrics` function from `collector.py`, so each live iteration, it can
collect the data, making both modules disconnected from each other.

[test_collector.py]
When I finished the display and main, I started making `test_collector.py`. The only problem
I ran through is what I described on the `_stats.py` explanation,

[logger.py]
I had the most fun creating this module.
By doing a similar thing I've done in `display.py`, I can get the same function
and collect the data, but this time save it to a file instead of displaying it.
I chose to save to the file each iteration, but I could've just make a dict (for example)
and append to it each iteration and then flush on finish, the problem with that, at a certain point,
it can be very heavy on the memory, because I save the data in the memory, so I decided to just save it each iteration.
At the start of the logger, I saved with timestamps but they weren't really grouping (for json), meaning
that all the entries from one date, weren't grouped together, so later, I decided to change that -
I made the logger save the data (in json) as the date (parent) and then hour-minutes-seconds and then the data,
making it way easier to create the `report.py` module way easier and having the data more readable.

[arguments]
I created all of the required arguments initially (`--interval`, `--log`) and on later commits I added 
`--format`, `--date`, `--cpu-warn`, `--mem-warn`. 
At the start, I thought I didn't need `--format` because I can just get the file extension in the path
provided by `--log` but after a few minutes I realised that if a path is not provided, it won't know
what format to create the file (it will always be json because its the default), so my change was
if the log was provided, get the file extension and if not, get the file extension with format.
The format cannot be None, because the default is json, so if its not provided, it automatically will be log.json.
I also added a message to the keyboard interrupt.

[test_logger.py]
This module was straightforward to make, only later I needed to scale it because 
I scaled the logger moodule.

[collector.py]
Added the network stats which were easy to add, needed to change a bit the test_collector module
but it was also straightforward.

[QoL]
Made the data be more readable in the log files too, making it be in 
Gigabytes or in Gibibytes.

[reports.py]
I already explained the steps I took to have this work, other than those steps, I only needed
to add a function that will create a table for the report, to make it readable.

