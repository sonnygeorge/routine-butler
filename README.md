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

## 👾 To-Do

### User Experience Improvements

- [ ] 👤 Make it so User is cached to file and auto-login occurs on start-up (meaning user can only log out via a log-out button that can be created later)
- [ ] 🎹 Implement/Enable something like [a custom Vue component](https://www.npmjs.com/package/vue-virtual-keyboard) or [Linux Matchbox](https://www.npmjs.com/package/vue-virtual-keyboard) touchscreen keyboard
- [ ] 🗑️❓ Implement "are you sure you want to _____" pop-ups for deleting things, starting routines
- [ ] 🔌📰 Write plugin documentation & display it in `ProgramConfigurer` UI
- [ ] 🚥 If user is supposed to be doing a routine when app fires up, redirect to where they were in the routine
- [ ] 🕙🔜 Implement system that queues routines? (e.g. routine_x is triggered by and alarm at 4:00pm and routine_y is triggered right after at 4:01, it should be activated right after routine_x is completed)

### Trivial UI Improvements

- [ ] ✨ Make `PromptContinue` pretty
- [ ] 🗑️ Trashcan .png instead of "cancel" icon for delete buttons
- [ ] 🚥 Add "next-routine: {alarm time}" information to header... IN FACT: **create a reusable component that takes a displays a routine's: name, next active alarm, num elements, & target duration info in a condensed wat and use that in header & routine_configurer icon_expansion headerss**
- [ ] 🔲🔲 Navigation in header could be more intuitive -- I.E. look more like navigation tabs than icon buttons
- [ ] 🔵➡️⚫ When disabling switches, toggle the associated element colors to gray to visualize what is getting disabled

### Codebase improvements

- [ ] 💁⚠️ Code review from Lucas? Evan?
- [ ] 📺 Videos in `README.MD`
- [ ] 🤖 UI tests using a client like [screen.py](https://github.com/zauberzeug/nicegui/blob/main/tests/screen.py#L85) as appropriate
- [ ] Enum for Quasar event names?
- [ ] Enum for Quasar color aliases?

### Plugins

- [ ] 📺 **Youtube**  (W/ capacity for single specific video... "modes?")
- [ ] 🌆 **DrivePics** (Take a GDrive folder name and randomly shows `n` pics in succession)
- [ ] 🔒 **LockBox**
- [ ] 🔓 **UnlockBox**
- [ ] 📄 **Flashcards**
- [ ] ⚖️ **MeasureWeight** (using WiiFit board)
- [ ] 📕🗣️ ...read stuff outloud ... audiobooks?
- [ ] 🎵 ...play music?
- [ ] 🧑‍🚀🗣️ ..."captains log" speech-to-text journaling
- [ ] 📷 ...take a pic with webcam and upload to given GDrive folder
- [ ] 🏋️‍♂️ ...CV-counted/monitored pushups & other physical exercisess

### Other

- [ ] 🛢️💾 DB backups to GDrive!
- [ ] 🤖📕 Scrape Valetta for flashcards
- [ ] 📊 Usage dashboards
