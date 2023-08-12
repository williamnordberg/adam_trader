#!/usr/bin/env python3
import time
import subprocess
import tkinter as tk


def send_notification(title, message):
    subprocess.run(['notify-send', title, message])


def update_session(name, duration, instructions, user_input, session_label, timer_label):
    session_label.config(text=f"{name}\n{instructions}", font=("Helvetica", 16))
    end_time = time.time() + duration * 60
    is_paused = False
    pause_time = 0

    def check_timeout():
        nonlocal end_time, pause_time, is_paused

        # Pause logic
        if 'pause' in user_input and not is_paused:
            user_input.remove('pause')
            is_paused = True
            pause_time = time.time()  # Save the pause time
            timer_label.config(text="Paused", font=("Helvetica", 14))

        # Resume logic
        if 'resume' in user_input and is_paused:
            user_input.remove('resume')
            end_time += time.time() - pause_time  # Update the end time based on the pause duration
            is_paused = False

        # If paused, skip the rest of the loop
        if is_paused:
            timer_label.after(1000, check_timeout)
            return

        remaining_time = int(end_time - time.time())
        minutes, seconds = divmod(remaining_time, 60)
        timer_label.config(text=f"Time Remaining: {minutes}:{seconds:02}", font=("Helvetica", 14))

        if remaining_time <= 0 or 'skip' in user_input:
            if 'skip' in user_input:
                send_notification("Skipped", f"To the next session: {name}")
                user_input.remove('skip')

            send_notification("Finished", name)
            user_input.append('timeout')
        else:
            timer_label.after(1000, check_timeout)

    check_timeout()


def pomodoro_workout():
    exercises = [
        "Warm-Up and Stretching",
        "Upper Body: Push-Ups",
        "Lower Body: Squats",
        "Core: Plank",
        "Upper Body: Tricep Dips",
        "Lower Body: Lunges",
        "Core: Bicycle Crunches",
        "Full Body: Burpees",
        "Upper Body: Shoulder Taps",
        "Lower Body: Step-Ups",
        "Core: Russian Twists",
        "Full Body: Mountain Climbers",
        "Upper Body: Diamond Push-Ups",
        "Lower Body: Glute Bridges",
        "Core: Leg Raises",
        "Cool Down and Stretching",
    ]

    def on_iconify(event):
        root.withdraw()

    root = tk.Tk()
    root.title("PomoFit")
    root.bind("<Unmap>", on_iconify)  # Bind the minimize event to the on_iconify function
    pause_button = tk.Button(root, text="Pause", command=lambda: user_input.append('pause'), font=("Helvetica", 12))
    pause_button.pack()
    resume_button = tk.Button(root, text="Resume", command=lambda: user_input.append('resume'), font=("Helvetica", 12))
    resume_button.pack()
    skip_button = tk.Button(root, text="Skip", command=lambda: user_input.append('skip'), font=("Helvetica", 12))
    skip_button.pack()
    session_label = tk.Label(root, text="", font=("Helvetica", 16))
    session_label.pack()
    timer_label = tk.Label(root, text="", font=("Helvetica", 14))
    timer_label.pack()

    focus_count = 1
    user_input = []

    for exercise in exercises:
        user_input.clear()

        update_session(f"Focus session {focus_count}", 25, "", user_input,
                       session_label, timer_label)
        while 'timeout' not in user_input:
            root.update()
            time.sleep(1)

        user_input.clear()

        update_session(exercise, 5, "", user_input, session_label, timer_label)
        while 'timeout' not in user_input:
            root.update()
            time.sleep(1)

        focus_count += 1

    root.mainloop()


if __name__ == '__main__':
    pomodoro_workout()
