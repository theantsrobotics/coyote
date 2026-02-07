# Coyote
Coyote is a simple GUI-based tool to generate autonomous paths for FTC 
robotics. It can generate Java code files from the paths generated. All you 
need to do after is add motor control (e.g. make shooter motors run when in 
shooting position).

## Building
To install the needed dependencies, run the following in your favorite terminal
emulator:
```bash
python3 -m pip install -r requirements.txt
```
Then, run this to build the app using cx-Freeze:
```bash
python3 setup.py build
```
The executable will be somewhere in the `build` directory.

## Credits
- Team Juice 16236 for FTC field image

