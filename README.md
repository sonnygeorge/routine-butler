# RoutineButler


## 🚀 **1.** Understand the App I am Trying to Build, Its Use-Case, and the Problem it Solves

### 👾 **1.1** What is the App?

`RoutineButler` is an app that:

- 🥧 is designed to be run "kiosk-style" on a RaspberryPi connected to:

  - 📺 an LCD touchscreen interface

  - 📦 an electro-mechanically operated lockbox

- 🏋️‍♀️ administers user-set routines with incentives (such as unlocking the box)

### 👾 **1.2** Who would use it?

First and foremost, the app is for my own use (I have already built raspberry-pi+lockbox+touchscreen kiosk setup).

![picture of the lockbox and kiosk](https://i.imgur.com/64x0Byw.jpeg)

Nevertheless, I am trying to take into consideration the possibility that other people might want to use this app someday as well.

### 👾 **1.3** What does it do?

The app allows users to:

- 📝 configure routines
- 📝 configure programs
- 💪 have routines administered to them
- 🔒 lock their phone away as an incentive to complete routines

### 👾 TODO

- [ ] change nomenclature of routine_items to elements
- [ ] make elements a json field in routine (and not own table) where order is inferred from the order of the json list

### Old ERD Diagram

Here is my idea for the data model / domain model / ERD so far:

```mermaid
erDiagram
    user {
        id int PK
    }

    routine {
        id int PK
        title str
        is_archived bool
        target_duration timedelta
        user_id int FK
    }

    routine_run {
        id int PK
        start_time datetime
        end_time datetime
        target_duration timedelta
        routine_id int FK
    }

    alarm {
        id int PK
        hour int
        minute int
        annoy_volume int
        annoy_interval timedelta
        enabled bool
        routine_id int FK
    }

    program {
        id int PK
        title str
        is_archived bool
        program_plugin str
        user_id int FK
    }

    prompt_wait_continue_program {
        id int PK
        prompt str
        wait_time int
        program_id int FK
    }

    repeat_mantra_program {
        id int PK
        mantra str
        n_repeats int
        program_id int FK
    }

    memes_queue_program {
        id int PK
        n_memes int
        program_id int FK
    }

    program_run {
        id int PK
        start_time datetime
        end_time datetime
        program_id int FK
        routine_run_id int FK
    }

    prompt_wait_continue_run {
        id int PK
        time_until_continued timedelta
        program_run_id int FK
    }

    memes_queue_run {
        id int PK
        avg_view_time_per_meme timedelta
        program_run_id int FK
    }

    routine_item {
        id int PK
        order_index int
        priority_level str
        is_reward bool
        program_plugin str
        program_id int FK
        routine_id int FK
    }

    user ||--o{ routine : has
    user ||--o{ program : has
    user ||--o{ routine_run : has
    user ||--o{ program_run : has

    routine ||--o{ alarm : has
    routine ||--o{ routine_item : has

    prompt_wait_continue_program |o--|| program : "is the plugin-specific data for a"
    repeat_mantra_program |o--|| program : "is the plugin-specific data for a"
    memes_queue_program |o--|| program : "is the plugin-specific data for a"

    program ||--o{ program_run : has
    routine ||--o{ routine_run : has

    prompt_wait_continue_run |o--|| program_run : "is the plugin-specific data for a"
    memes_queue_run |o--|| program_run : "is the plugin-specific data for a"
```

- **NOTE:** "PromptWaitContinue", "RepeatMantra", and "MemesQueue" are just placeholder `ProgramPlugins` to help illustrate the idea... I might or might not implement them as suggested in the diagram... However, everything else is how I actually envision it as of now.
