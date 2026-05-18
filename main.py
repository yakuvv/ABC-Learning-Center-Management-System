import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import config
import database

ctk.set_appearance_mode("light")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(config.WINDOW_TITLE)
        self.geometry("1280x720")
        self.resizable(False, False)
        # Grey outer background
        self.configure(fg_color="#e5e5e5")

        # Initialize tracking assets
        self.frames = []
        self.frame_index = 0
        self.loading_label = None

        # Pre-load the animated loading GIF frames into cache memory
        self.load_gif_frames()

        self.center_window()
        self.create_login_ui()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 720) // 2
        self.geometry(f"1280x720+{x}+{y}")

    def load_gif_frames(self):
        # Checking where the script looks for the file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gif_path = os.path.join(current_dir, "assets", "loading_screen.gif")

        print("\n--- checking loading gif location ---")
        print(f"i am looking for the file here: {gif_path}")
        print(f"file exists status: {os.path.exists(gif_path)}")

        try:
            gif_obj = Image.open(gif_path)
            self.num_frames = gif_obj.n_frames
            print(f"found it, total frames: {self.num_frames}")

            self.frames = []
            for i in range(self.num_frames):
                gif_obj.seek(i)
                self.frames.append(ctk.CTkImage(light_image=gif_obj.copy(), dark_image=gif_obj.copy(), size=(150, 150)))
            print("cached all frames into memory successfully")
        except Exception as e:
            print(f"failed to load the gif: {e}")
            self.frames = None
        print("--------------------------------------\n")

    def create_login_ui(self):
        # card container with 0 corner radius to keep it sharp
        self.card = ctk.CTkFrame(self, width=650, height=360, fg_color="#121858", corner_radius=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)  # Prevent frame resizing

        # Sign In Title with Left-aligned using padx anchoring
        title = ctk.CTkLabel(self.card, text="Sign In",
                             font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
                             text_color="white", anchor="w")
        title.pack(fill="x", padx=35, pady=(35, 15))

        # Input Field Stylings
        self.username_entry = ctk.CTkEntry(self.card,
                                           placeholder_text="Email or Username",
                                           placeholder_text_color="#9fa3c0",
                                           text_color="white",
                                           fg_color="transparent",
                                           border_color="white",
                                           border_width=2,
                                           corner_radius=0,
                                           width=580, height=40,
                                           font=ctk.CTkFont(family="Arial", size=14))
        self.username_entry.pack(padx=35, pady=10, anchor="w")

        self.password_entry = ctk.CTkEntry(self.card,
                                           placeholder_text="Password",
                                           placeholder_text_color="#9fa3c0",
                                           text_color="white",
                                           show="*",
                                           fg_color="transparent",
                                           border_color="white",
                                           border_width=2,
                                           corner_radius=0,
                                           width=580, height=40,
                                           font=ctk.CTkFont(family="Arial", size=14))
        self.password_entry.pack(padx=35, pady=10, anchor="w")

        # Buttons Container - Right aligned to match the image layout
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=35, pady=(20, 0), anchor="e")

        # Right packing places buttons side-by-side on the right margin
        login_btn = ctk.CTkButton(btn_frame, text="LOG IN",
                                  width=140, height=45,
                                  fg_color="#0f3afc",
                                  hover_color="#0b2ecb",
                                  text_color="white",
                                  corner_radius=18,
                                  font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                                  command=self.login)
        login_btn.pack(side="right", padx=(10, 0))

        close_btn = ctk.CTkButton(btn_frame, text="CLOSE",
                                  width=140, height=45,
                                  fg_color="#e5e5e5",
                                  hover_color="#cdcdcd",
                                  text_color="black",
                                  corner_radius=18,
                                  font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
                                  command=self.destroy)
        close_btn.pack(side="right", padx=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter email/username and password")
            return

        conn = database.get_connection()
        cursor = conn.cursor()

        # Check Staff/Admin
        cursor.execute("""
                       SELECT staffID, staffFname, staffLname
                       FROM STAFF
                       WHERE email = ?
                         AND password = ?
                       """, (username, password))
        staff = cursor.fetchone()

        if staff:
            full_name = f"{staff['staffFname']} {staff['staffLname']}"
            conn.close()
            # Transition to loading animation screen first
            self.show_loading_screen("Admin/Staff", full_name)
            return

        # Check Tutor
        cursor.execute("""
                       SELECT tutorID, tutorFname, tutorLname
                       FROM TUTOR
                       WHERE tutorEmail = ?
                         AND password = ?
                       """, (username, password))
        tutor = cursor.fetchone()

        if tutor:
            full_name = f"{tutor['tutorFname']} {tutor['tutorLname']}"
            conn.close()
            # Transition to loading animation screen first
            self.show_loading_screen("Tutor", full_name)
            return

        conn.close()
        messagebox.showerror("Login Failed", "Invalid email or password")

    def show_loading_screen(self, role, name):
        # hiding the form elements to switch screens
        self.card.place_forget()

        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

        self.update()

        if self.frames:
            self.animate_gif()
            # holding the animation scene for 2.5 seconds before launching dashboard
            self.after(2500, lambda: self.launch_dashboard(role, name))
        else:
            self.launch_dashboard(role, name)

    def animate_gif(self):
        if self.loading_label and self.loading_label.winfo_exists():
            current_frame = self.frames[self.frame_index]
            self.loading_label.configure(image=current_frame)

            self.frame_index = (self.frame_index + 1) % len(self.frames)
            # keeping refresh timer at 80ms for performance stability
            self.after(80, self.animate_gif)

    def launch_dashboard(self, role, name):
        self.destroy()
        from dashboard import Dashboard
        dashboard = Dashboard(user_role=role, user_name=name)
        dashboard.mainloop()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
