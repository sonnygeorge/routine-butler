# RoutineButler

## 👾 What is the App?

`RoutineButler` is an app that:

- 🥧 is designed to be run "kiosk-style" on a RaspberryPi connected to:

  - 📺 an LCD touchscreen interface

  - 📦 an electro-mechanically operated lockbox

- 🏋️‍♀️ administers user-set routines with incentives (such as unlocking the box)

## 👾 Who would use it?

First and foremost, the app is for my own use (I have already built the raspberry-pi+lockbox+touchscreen kiosk setup).

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

Nevertheless, I am trying to take into consideration the possibility that other people might want to use this app someday as well.

## 👾 What does it do?

The app allows users to:

- 📝 configure routines
- 📝 configure programs
- 💪 have routines administered to them
- 🔒 lock something (e.g. the user's phone) away as an incentive to complete routines

## 👾 TODO

- [ ] Add **views folder** and add views: configure_routines, configure_programs, administer_routines, login, home
- [ ] **components folder** with components
- [ ] **components/primitives** folder with primitives
- [ ] **components/micro** folder with microcomponents
- [ ] **state object** w/ header, engine, and user ... (clean up main)

...

- [ ] Evaluate typed dict for dataclasses... [pydantic alternative](https://roman.pt/posts/pydantic-in-sqlalchemy-fields/)
- [ ] Evaluate/get feedback on UI handlers / object strategy / naming / ui constant centralization strategy
- [ ] UI tests using: [screen.py](https://github.com/zauberzeug/nicegui/blob/main/tests/screen.py#L85)
- [x] Implement [trailing](https://nicegui.io/documentation/slider#throttle_events_with_leading_and_trailing_options) throttling where appropriate
