# Insomnia

A tool that can prevent Windows from turning off your screen / sleeping for a while.

## Usage

```
insomnia [-d] [-t <milliseconds> | <command>]
```

`-d`: Your monitor won't turn off.

*Without the argument above, your screen will turn off as usual, but your system won't sleep.*

`-t <milliseconds>`: Program will run for `TIME` milliseconds, you can press <kbd>Esc</kbd> any time to stop it.

`<command>`: Do not turn off the monitor / sleep until the end of command execution.

*Without the two arguments above, the program will keep running until you press <kbd>Esc</kbd>.*
