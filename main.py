import kivymd.uix.button
from kivymd.uix.button import MDRectangleFlatButton, MDFillRoundFlatButton
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
import speech_recognition as sr
import threading
from kivy.uix.image import Image
from kivymd.uix.button import MDIconButton
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp


Window.size = (480, 800)

font_path = "C:/Users/anisi/PycharmProjects/Kyvi/19168.ttf"
background_image_path = "C:/Users/anisi/PycharmProjects/Kyvi/1636777431_76-modnica-club-p-krasivii-goluboi-fon-odnotonnii-81.jpg"
dialog_background_image_path = "C:/Users/anisi/PycharmProjects/Kyvi/1636777431_76-modnica-club-p-krasivii-goluboi-fon-odnotonnii-81.jpg"

KV = f'''
BoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(10)

    canvas.before:
        Rectangle:
            size: self.size
            pos: self.pos
            source: "{background_image_path}"

    MDLabel:
        id: label
        text: "Нажмите кнопку для записи"
        valign: "top"
        halign: "center"
        text_size: self.size
        font_name: "{font_path}"
        font_size: "32sp"
        color: 1, 1, 1, 1  # Черный цвет текста

    MDIconButton:
        id: record_button
        icon: "StartButton.png"
        icon_size: "150dp"
        pos_hint: {{ "center_x": 0.5 }}
        on_release: app.start_recording_thread()

    MDRectangleFlatButton:
        text: "Показать записи"
        pos_hint: {{ "center_x": 0.5 }}
        font_name: "{font_path}"
        font_size: "20sp"
        text_color: 1, 1, 1, 1  # Белый цвет текста
        md_bg_color: 0.129, 0.588, 0.952, 1  # Синий цвет фона кнопки
        on_release: app.show_diary()
        line_color: 0.4, 0.3, 0.7, 1  # Цвет границы кнопк
        
    
'''

class VoiceDiaryApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_recording = False
        self.stop_recording = False
        self.recognizer = sr.Recognizer()
        self.audio = None

    def build(self):
        return Builder.load_string(KV)

    def start_recording_thread(self):
        if self.is_recording:
            # Если запись уже идет, останавливаем её
            self.stop_recording = True
            self.root.ids.label.text = "Запись остановлена. Обработка..."
        else:
            # Если запись не идет, начинаем новую запись
            self.stop_recording = False
            self.is_recording = True
            threading.Thread(target=self.start_recording).start()

    def start_recording(self):
        self.root.ids.label.text = "Говорите..."
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                # Начинаем запись с возможностью остановки
                self.audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                if self.stop_recording:
                    # Если запись остановлена, сохраняем уже записанное аудио
                    self.is_recording = False
                    self.root.ids.label.text = "Запись остановлена. Обработка..."
                    self.process_audio()
                    return

                # Если запись не была остановлена, обрабатываем аудио
                self.process_audio()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            self.root.ids.label.text = f"Ошибка: {e}"
        finally:
            self.is_recording = False

    def process_audio(self):
        try:
            if self.audio:
                # Распознаем текст из аудио
                text = self.recognizer.recognize_google(self.audio, language="ru-RU")
                self.save_to_diary(text)
                self.root.ids.label.text = "Запись сохранена"
        except sr.UnknownValueError:
            self.root.ids.label.text = "Не удалось распознать речь."
        except sr.RequestError as e:
            self.root.ids.label.text = f"Ошибка сервиса распознавания: {e}"
        except Exception as e:
            self.root.ids.label.text = f"Ошибка: {e}"

    def save_to_diary(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("diary.txt", "a", encoding="utf-8") as file:
            file.write(f"{timestamp} - {text}\n")

    def show_diary(self):
        try:
            with open("diary.txt", "r", encoding="utf-8") as file:
                entries = file.readlines()
            diary_content = ''.join(entries)
            if diary_content:
                self.show_dialog(diary_content)
            else:
                self.show_dialog("Дневник пуст.")
        except FileNotFoundError:
            self.show_dialog("Дневник пуст.")

    def show_dialog(self, content):
        dialog_text = content

        scroll_view = ScrollView(
            size_hint=(1, None),
            size=(Window.width * 0.8, Window.height * 0.4)
        )

        label = Label(
            text=dialog_text,
            size_hint_y=None,
            markup=True,
            color=(0, 0, 0, 1),
            font_size="16sp",
            halign="left",
            valign="top",
            padding=(dp(10), dp(10))
        )

        label.bind(
            width=lambda *x: label.setter('text_size')(label, (label.width, None)),
            texture_size=lambda instance, size: setattr(instance, 'height', size[1])
        )

        scroll_view.add_widget(label)

        input_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100))
        input_field = MDTextField(
            hint_text="Введите №записи для удаления",
            size_hint=(1, None),
            height=dp(50),
            font_size="16sp",
            mode="rectangle"
        )
        input_layout.add_widget(input_field)

        delete_button_layout = AnchorLayout(anchor_x="right", anchor_y="top", size_hint_y=None, height=dp(50))
        delete_button = MDRectangleFlatButton(
            text="Удалить запись",
            text_color=(1, 1, 1, 1),
            line_color=(1, 0, 0, 1),
            md_bg_color=(1, 0, 0, 1),
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            on_release=lambda x: self.delete_specific_entry(input_field.text, dialog)
        )
        delete_button_layout.add_widget(delete_button)

        content_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=Window.height * 0.6)
        content_layout.add_widget(delete_button_layout)
        content_layout.add_widget(scroll_view)
        content_layout.add_widget(input_layout)

        dialog = MDDialog(
            title="Записи",
            type="custom",
            content_cls=content_layout,
            size_hint=(0.8, None),
            height=Window.height * 0.7,
            buttons=[
                MDRectangleFlatButton(
                    text="Удалить все записи",
                    text_color=(1, 1, 1, 1),
                    line_color=(1, 0, 0, 1),
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.delete_diary(dialog)
                ),
                MDRectangleFlatButton(
                    text="Закрыть",
                    text_color=(1, 1, 1, 1),
                    line_color=(0.129, 0.588, 0.952, 1),
                    md_bg_color=(0.129, 0.588, 0.952, 1),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )

        dialog.open()

    def delete_diary(self, dialog):
        try:
            with open("diary.txt", "w", encoding="utf-8") as file:
                file.write("")
            dialog.dismiss()
            self.show_dialog("Дневник очищен.")
        except Exception as e:
            self.show_dialog(f"Ошибка удаления: {e}")

    def delete_specific_entry(self, entry_number, dialog):
        try:
            entry_number = int(entry_number)
            with open("diary.txt", "r", encoding="utf-8") as file:
                entries = file.readlines()

            if 1 <= entry_number <= len(entries):
                entries.pop(entry_number - 1)
                with open("diary.txt", "w", encoding="utf-8") as file:
                    file.writelines(entries)
                dialog.dismiss()
                self.show_dialog("Запись удалена.")
            else:
                self.show_dialog("Неверный номер записи.")
        except ValueError:
            self.show_dialog("Не корректный номер.")
        except Exception as e:
            self.show_dialog(f"Ошибка удаления: {e}")

if __name__ == "__main__":
    VoiceDiaryApp().run()