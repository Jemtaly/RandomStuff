# Boolfuck Verilog

An awesome boolfuck machine implemented in verilog.

## Compile and Run Testbench File

Run following commands in current path:

```
verilator --cc --exe --build main.cpp boolfuck.v -LDFLAGS -static
obj_dir/Vboolfuck.exe
```

*Notice: You need to install verilator in msys2 to compile it.*

## Usage

| Key | while your bf program is stopped | while your bf program is running | while your bf program is waiting for an input | when your bf program has output one bit and is waiting for user confirmation |
| --- | --- | --- | --- | --- |
| Left | move the cursor left | | | |
| Right | move the cursor right | | | |
| Space | run your bf program | halt | halt | halt |
| `/` | input a "halt" instruction at the current position of the cursor | | input `0` | confirm |
| `~` `<` `>` `,` `.` `[` `]` | input the corresponding command at the current position of the cursor | | input `1` | confirm |
