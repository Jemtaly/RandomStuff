# WinUtils

## Insomnia

A tool that can prevent Windows from turning off your screen / sleeping for a while.

### Usage

```
Description: Prevent the PC from sleeping.
Usage: insomnia.exe [-d] [-t <ms> | -c <cmd>]
Options:
  -d        prevent the display from sleeping as well
  -t <ms>   wait for <ms> milliseconds
  -c <cmd>  execute <cmd> and wait for it to finish
```

`-d`: Your monitor won't turn off.

*Without the argument above, your screen will turn off as usual, but your system won't sleep.*

`-t <ms>`: Program will run for `<ms>` ms, you can press <kbd>Esc</kbd> any time to stop it.

`-c <cmd>`: Do not turn off the monitor / sleep until the end of command execution.

*Without the two arguments above, the program will keep running until you press <kbd>Esc</kbd>.*

## HotKey

Use Alt+F1, Alt+F2 and Alt+F3 on your keyboard to simulate the left, middle and right mouse buttons respectively. Which is useful when you are using the touchpad and want to perform a "press centre button or right button drag and drop" operation.
