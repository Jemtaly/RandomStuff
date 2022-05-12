# CellAuto

A cellular automata written in C++.

![screenshot](/C++/CellAuto/screenshot.gif)

## Usage

```
cellauto [-b] [-r RULE] [-n H W] or cellauto FILENAME
```

## Control

| Key | Usage |
| --- | --- |
| <kbd>Space</kbd> | Run/Stop |
| <kbd>`</kbd> | Next Generation |
| <kbd>,</kbd> | Undo |
| <kbd>.</kbd> | Redo |
| <kbd>h</kbd> | Back to the first generation |
| <kbd>e</kbd> | Go to the last generation |
| <kbd>b</kbd> | Set/Unset Bound |
| <kbd>w</kbd> <kbd>a</kbd> <kbd>s</kbd> <kbd>d</kbd> | move current loction |
| <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> | move space (disabled when bound is setted) |
| <kbd>1</kbd> | Revive current cell |
| <kbd>0</kbd> | Kill current cell |
| <kbd>8</kbd> | Flip the state of the current cell |
| <kbd>c</kbd> | Clear space |
| <kbd>r</kbd> | Generate space randomly |
| <kbd>R</kbd>+<kbd>Num</kbd> | Generate space randomly with a coefficient (Num / 8) |
| <kbd>m</kbd> | Go to menu |
