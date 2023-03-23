# 🚀 Cassius

```python
╔═════════════════════════════════════════════════════════════╗
║ .▄████▄. .▄▄▄ . . . .██████ . ██████ .██░ █▓. .██ . ██████. ║
║ ▒██▀ ▀█. ▒████▄ . .▒██ . .▒ ▒██. .▒▒ ░██░ ██. ░██░ ██▒ . ▒. ║
║ ▒▓█. . ▄ ▒██. ▀█▄ .░ ▓██▄ . ░ ▓██▄ . ▒██░.██. ▒██░. ▓██▄. . ║
║ ▒▓▓▄ ▄██▒░██▄▄▄▄██ . ▒ .░██▒. ▒ .░██▒░██░░▓█. ░██░. ▒ .░██▒ ║
║ ▒ ▓███▀ ░ ▓█ . ▓██▒▒██████▒░.██████▒▒░██░░▒█████▓ ▒██████▒▒ ║
║ ░ ░▒ ▒ .░ ▒▒ . ▓▒█░▒ ▒▓▒ ▒░░▒ ▒▓▒ ▒ ░░▓. ░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░ ║
║ . .░ ▒ .▒ . ▒▒ ░░ ░▒. ░. ▒░░▒ .░.░ ▒.░░░▒░ ░ ░ ░ ░▒ ░░ ░░ . ║
║ ░. . . . . ░ . ▒. .░ .░. ░░ ░ .░. ░ . ▒ ░ ░░░ ░ ░ ░ ░░ .░ . ║
║ ▒ ░. . .░. . . ░. ░. . . ░. . . . ░ . ░ . . ░ . . . ░. .░ . ║
╚═════════════════════════════════════════════════════════════╝
```

## TODO

- [ ] Somehow implement an abc of protocol to more formally/logistically enforce models to have an id primary key
- [ ] pre-commit hooks
- [ ] Get DB Wrapper roasted?
- [ ] Seperate models into their own files
- [ ] Add "program" entities to the app: two very simple ones could be "readtext" and "promptcontinue"
- [ ] Add functionality to check for actively scheduled routines and run them with alarm sound at beginning
- [ ] Document everything with doc strings, mermaid diagrams, etc.
- [ ] Get a full-on, paid code review from one or more relevant people

## ❓ About

This repo contains the WIP "kiosk-style" app that I will run on my raspberry pi and use to accomplish a variety of tasks including but not limited to:

- entertainment (limited watching of videos, etc.)
- controlling mechanical devices such as a lockbox for downtime from electronics
- other interactive sub-apps such as: computer-vision-monitored physical exercise, personal study tools like flashcards, etc.

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

## 📉 Current Status

I have successfully written an app structure that seems to accomplish the current goal.

Currently working toward an MVP that I will use as an alarm clock and perhaps get formally code reviewed.
