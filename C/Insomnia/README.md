# Insomnia

A tool that can prevent Windows from turning off your screen / sleeping for a while.

## Usage

```
Description: Prevent the PC from sleeping.
Usage: insomnia [-d] [-t <ms> | <cmd>]
Options:
  -d       prevent the display from sleeping as well
  -t <ms>  wait for <ms> milliseconds
  <cmd>    execute <cmd> and wait for it to finish
```

`-d`: Your monitor won't turn off.

*Without the argument above, your screen will turn off as usual, but your system won't sleep.*

`-t <ms>`: Program will run for `<ms>` ms, you can press <kbd>Esc</kbd> any time to stop it.

`<cmd>`: Do not turn off the monitor / sleep until the end of command execution.

*Without the two arguments above, the program will keep running until you press <kbd>Esc</kbd>.*
