# RPN Compiler

This project is a compiler of a RPN-based language, with programs that work with syntax such as:

```
(10 0 +)
(5 0 +)
(3 0 +)
( (2 RES) ( ((3 RES) 1 -) (1 RES) * ) + )
( ( (4 RES) ( (3 RES) (1 RES) + ) * ) 2 | )
```

# Getting started

After cloning this repository, the first thing to do is installing the required python libraries. To achieve this, follow these steps:

1. Create a virtual environment:
```python
python3 -m venv .venv
```

2. Enable the virtual environment:
```python
source .venv/bin/activate
```

3. Install dependencies:
```python
pip install -r requirements.txt
```

With the dependencies downloaded, you can now run the project with a file as input by command line:
```python
python main.py <input_file>
```

By default, the semantic analyzer will have automatic type casting enabled. This means that expressions such as `(20 0.5 +)` won't raise any errors, since 20 will be automatically cast to a floating point number.

To disable automatic type casting, run the program with the flag `--no-cast`, like this:
```python
python main.py <input_file> --no-cast
```

This will cause errors at compile time when different types are combined in an operation, such as in the previous example (INT and FLOAT).

# Running in an Arduino

The project contains a bash script called `upload_to_arduino.sh`, which will build the project and upload it to an arduino automatically. However, you will need to configure the desired port to communicate to it. This can be done by changing the `PORT` parameter in the script:
```bash
PORT="/dev/cu.usbserial-A5069RR4"
```

With this, you can access the results sent by arduino with an app like macos's `screen`:
`screen <PORT> 2400`
note: you might have to adjust the BAUDRATE parameter, both in screen and the script.
