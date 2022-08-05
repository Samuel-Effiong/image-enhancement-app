
"""The Controller

The view module will control the functionality of the app
and ensures that every thing runs efficiently and in a tip top manner

It boots up the app interface and manage the interaction between the
view and the model, the user will only have access to the view
while the model and view are encapsulated

"""

import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap


from maininterface import MainInterface, EnlargeImageInterface, AboutInterface
from model import Model


class Controller(object):
    """Will coordinate the interaction between the MainInterface and the Model, thereby having
    access to both"""
    def __init__(self):
        # initialize the view
        self.init_view()
        self.init_model()
        self.handle_file_menu_interactions()
        self.handle_tool_menu_interactions()
        self.handle_miscellaneous_signal()

    def init_view(self):
        self.view = MainInterface()
        self.view.show()

    def init_model(self):
        self.model = Model()
        self.model.activate_disable_menu_actions(self.view)

    def handle_file_menu_interactions(self):
        self.view.action_open_new_image.triggered.connect(
            lambda: self.model.open_image(self.view))
        self.view.action_rename_image.triggered.connect(
            lambda: self.model.rename_image(self.view))
        self.view.action_save.triggered.connect(
            lambda: self.model.save_image(self.view))
        self.view.action_quit.triggered.connect(
            lambda event: self.model.exit_app(self.view, event))
        self.view.action_about.triggered.connect(
            lambda: self.model.open_about_dialog(AboutInterface()))

    def handle_tool_menu_interactions(self):
        # only initialize dialog box when needed
        self.view.action_image_enlargement.triggered.connect(
            lambda: self.model.open_enlargement_dialog_box(EnlargeImageInterface(self.view)))

    def handle_miscellaneous_signal(self):
        self.view.miscellaneous_event.resize.connect(lambda: self.model.resize_image(self.view))
        self.view.miscellaneous_event.keypress.connect(lambda event: self.model.navigate_image(event, self.view))
        self.view.miscellaneous_event.exit_signal.connect(lambda event: self.model.exit_app(self.view, event))
        self.view.miscellaneous_event.enlargement_signal.connect(
            lambda interpolation, upscale, filename: self.model.enlarge_image(
                self.view, interpolation=interpolation, upscale=upscale, filename=filename))
        self.view.miscellaneous_event.enlargement_finished.connect(
            lambda: self.model.end_of_enlargement_notification(self.view)
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # set the application details
    app.setApplicationName("Thera")
    app.setOrganizationName("Nkopuruk Samuel E.")
    app.setOrganizationDomain("www.example.com")

    # setup splashscreen
    pixmap = QPixmap()
    splash_screen = QSplashScreen(pixmap)
    controller = Controller()
    splash_screen.finish(controller.view)
    sys.exit(app.exec())
