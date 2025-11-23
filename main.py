
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
import threading, os, time

from sos_logic import (
    ensure_app_dirs, load_config, save_config,
    get_location_ipinfo, send_email, send_telegram
)
from util_camera import capture_photo
from util_audio_recorder import AndroidAudioRecorder

KV = """
#:import dp kivy.metrics.dp
<SOSScreen>:
    name: "sos"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16); spacing: dp(12)

        Label:
            text: "🚨 زر الطوارئ"
            font_size: "28sp"
            size_hint_y: None
            height: dp(48)

        Label:
            id: status_lbl
            text: root.status_text
            font_size: "16sp"
            size_hint_y: None
            height: dp(28)

        Button:
            text: "SOS"
            font_size: "28sp"
            size_hint_y: None
            height: dp(80)
            background_normal: ""
            background_color: (1, 0, 0, 1)
            on_release: root.on_sos()

        Widget:
            size_hint_y: 1

        BoxLayout:
            size_hint_y: None; height: dp(50); spacing: dp(10)
            Button:
                text: "الإعدادات"
                on_release: app.sm.current = "settings"
            Button:
                text: "خروج"
                on_release: app.stop()

<SettingsScreen>:
    name: "settings"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16); spacing: dp(10)

        Label:
            text: "الإعدادات"
            font_size: "24sp"
            size_hint_y: None; height: dp(40)

        GridLayout:
            cols: 2
            row_default_height: dp(40)
            row_force_default: True
            spacing: dp(8)

            Label: text: "البريد المرسل:"
            TextInput:
                id: email_in
                text: root.email
                multiline: False

            Label: text: "كلمة مرور التطبيق:"
            TextInput:
                id: pass_in
                text: root.password
                password: True
                multiline: False

            Label: text: "رقم الطوارئ:"
            TextInput:
                id: emer_in
                text: root.emergency_number
                multiline: False

            Label: text: "Bot Token (Telegram):"
            TextInput:
                id: tg_token_in
                text: root.tg_token
                multiline: False

            Label: text: "Chat ID (Telegram):"
            TextInput:
                id: tg_chat_in
                text: root.tg_chat
                multiline: False

            Label: text: "جهات الاتصال (Emails مفصولة بفواصل):"
            TextInput:
                id: contacts_in
                text: root.contacts_csv
                multiline: False

        BoxLayout:
            size_hint_y: None; height: dp(48); spacing: dp(10)
            Button:
                text: "حفظ"
                on_release: root.on_save(
                    email_in.text, pass_in.text, emer_in.text,
                    tg_token_in.text, tg_chat_in.text, contacts_in.text
                )
            Button:
                text: "رجوع"
                on_release: app.sm.current = "sos"
"""

class SOSScreen(Screen):
    status_text = StringProperty("جاهز")

    def on_pre_enter(self):
        self.status_text = "جاهز"

    def on_sos(self):
        threading.Thread(target=self._run_sos_flow, daemon=True).start()

    def _run_sos_flow(self):
        try:
            ensure_app_dirs()
            cfg = load_config()

            self._set_status("تسجيل الصوت ...")
            audio_path = os.path.join(App.get_running_app().app_dir, "sos_audio.m4a")
            rec = AndroidAudioRecorder(audio_path=audio_path)
            started = rec.start()
            if not started:
                self._set_status("تعذر بدء التسجيل الصوتي")

            self._set_status("التقاط صورة ...")
            photo_path = os.path.join(App.get_running_app().app_dir, "sos_image.png")
            ok = capture_photo(photo_path)
            if not ok:
                self._set_status("تعذر التقاط صورة، سيُرسل التنبيه بدون صورة.")

            time.sleep(5)

            self._set_status("إيقاف التسجيل الصوتي ...")
            rec.stop()

            self._set_status("جلب الموقع ...")
            location = get_location_ipinfo()

            contacts = cfg.get("contacts", [])
            if cfg.get("email") and cfg.get("password") and contacts:
                self._set_status("إرسال البريد ...")
                send_email(cfg, location, None, audio_path if os.path.exists(audio_path) else None, photo_path if os.path.exists(photo_path) else None, "")

            self._set_status("إرسال تيليجرام ...")
            tg_text = f"🚨 SOS\nالموقع: {location}"
            send_telegram(cfg, tg_text, None, audio_path if os.path.exists(audio_path) else None, photo_path if os.path.exists(photo_path) else None)

            self._set_status("تم الإرسال ✅")
        except Exception as e:
            self._set_status(f"خطأ: {e}")

    def _set_status(self, txt):
        Clock.schedule_once(lambda dt: setattr(self, "status_text", txt), 0)


class SettingsScreen(Screen):
    email = StringProperty("")
    password = StringProperty("")
    emergency_number = StringProperty("911")
    tg_token = StringProperty("")
    tg_chat = StringProperty("")
    contacts_csv = StringProperty("")

    def on_pre_enter(self):
        cfg = load_config()
        self.email = cfg.get("email","")
        self.password = cfg.get("password","")
        self.emergency_number = cfg.get("emergency_number","911")
        self.tg_token = cfg.get("telegram_bot_token","")
        self.tg_chat = cfg.get("telegram_chat_id","")
        self.contacts_csv = ",".join(cfg.get("contacts", []))

    def on_save(self, email, password, emer, tg_token, tg_chat, contacts_csv):
        cfg = load_config()
        cfg["email"] = email.strip()
        cfg["password"] = password.strip()
        cfg["emergency_number"] = emer.strip() or "911"
        cfg["telegram_bot_token"] = tg_token.strip()
        cfg["telegram_chat_id"] = tg_chat.strip()
        contacts = [c.strip() for c in contacts_csv.split(",") if c.strip()]
        cfg["contacts"] = contacts
        save_config(cfg)
        App.get_running_app().sm.current = "sos"


class SOSApp(App):
    def build(self):
        self.app_dir = ensure_app_dirs()
        self.sm = ScreenManager()
        self.sm.add_widget(SOSScreen())
        self.sm.add_widget(SettingsScreen())
        Builder.load_string(KV)
        if platform != "android":
            Window.size = (420, 760)
        return self.sm

if __name__ == "__main__":
    SOSApp().run()
