
import typing
from PyQt6.QtWidgets import (QLabel, QPushButton, QMainWindow, QMenuBar,
                             QStatusBar, QDialog, QRadioButton, QGroupBox,
                             QHBoxLayout, QComboBox, QVBoxLayout,
                             QSizePolicy, QDialogButtonBox, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal
from PyQt6.QtGui import (
    QFont, QAction, QIcon, QKeySequence, QResizeEvent, QKeyEvent, QPixmap,
    QCloseEvent
)


class MiscellaneousEvent(QObject):
    resize = pyqtSignal(QSize)
    keypress = pyqtSignal(QKeyEvent)
    exit_signal = pyqtSignal(QCloseEvent)
    interpolation_signal = pyqtSignal(str)
    enlargement_signal = pyqtSignal(str, tuple, str)
    enlargement_finished = pyqtSignal()


class MainInterface(QMainWindow):
    def __init__(self, parent=None):
        super(MainInterface, self).__init__(parent)
        self.setup_window()

        self.setup_menubar()
        self.setup_status_bar()
        self.setup_central_widget()

        self.miscellaneous_event = MiscellaneousEvent()

    def setup_window(self):
        self.setWindowTitle("Thera")
        self.setObjectName("TheView")
        self.setMinimumSize(QSize(800, 700))

        self.main_font = self.setup_font(font_family="Verdana", point_size=10)
        self.setFont(self.main_font)

    def setup_menubar(self):
        """Add menu bar to the application containing different actions
        """
        self.menu_bar = QMenuBar(self)

        # Add the File menu to the menu bar
        self.menu_file = self.menu_bar.addMenu("File")
        self.menu_file.setFont(self.main_font)

        self.action_open_new_image = self.create_actions("Open Image", QKeySequence.StandardKey.Open,
                                                         tooltip="Open a new image")
        self.action_rename_image = self.create_actions("Rename", "Ctrl+R", tooltip="Rename image")
        self.action_save = self.create_actions("Save...", tooltip="Save image", shortcut=QKeySequence.StandardKey.Save)
        self.action_quit = self.create_actions("Exit", shortcut=QKeySequence.StandardKey.Quit,
                                               tooltip="Exit Image app")

        actions = [
            self.action_open_new_image, self.action_rename_image, 'separator',
            self.action_save, 'separator', self.action_quit
        ]
        self.add_actions_to_menu(menu=self.menu_file, actions=actions)

        # Add the Tools menu to the menu bar
        self.menu_tool = self.menu_bar.addMenu("Tools")
        self.menu_tool.setFont(self.main_font)

        self.action_image_enlargement = self.menu_tool.addAction("Increase image size")
        self.action_image_enlargement.setFont(self.main_font)

        self.action_about = self.create_actions("About", shortcut=QKeySequence.StandardKey.HelpContents)

        self.menu_bar.addAction(self.action_about)
        self.setMenuBar(self.menu_bar)

    def setup_status_bar(self):
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage("Ready", 5000)
        self.setStatusBar(self.status_bar)

    def setup_central_widget(self):
        self.image_container = QLabel("Hello, I am Thera")
        self.image_container.setFont(self.setup_font(font_family="Verdana", point_size=20,
                                                     bold=True, italic=True))
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_container)

        self.image_container.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.image_container.addActions(
            [self.action_save, self.action_rename_image,
             self.action_image_enlargement]
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.miscellaneous_event.resize.emit(event.size())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.miscellaneous_event.keypress.emit(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        # event.ignore()
        self.miscellaneous_event.exit_signal.emit(event)

    @staticmethod
    def setup_font(*, font_family=None, point_size=12, bold=False,
                   style=None, italic=False) -> QFont:
        font = QFont()
        if font_family:
            font.setFamily(font_family)
        if style:
            font.setStyle(style)

        font.setPointSize(point_size)
        font.setBold(bold)
        font.setItalic(italic)

        return font

    def create_actions(self, label, shortcut=None, icon=None, slot=None, checkable=None, tooltip=None) -> QAction:
        """Create the action of a menu using the given parameter and returns the action object"""
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(shortcut)
        if icon:
            action.setIcon(QIcon(icon))
        if slot:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(checkable)
        if tooltip:
            action.setToolTip(tooltip)
            action.setStatusTip(tooltip)
        return action

    @staticmethod
    def add_actions_to_menu(*, menu, actions: typing.Iterable[QAction]) -> None:
        [
            menu.addAction(action) if not isinstance(action, str) else menu.addSeparator()
            for action in actions
        ]


class EnlargeImageInterface(QDialog):
    def __init__(self, parent=None):
        super(EnlargeImageInterface, self).__init__(parent=parent)
        self.parent = parent

        ###########################################################

        warning_message = "This is an experimental feature and highly computer" \
                          " intensive, it might crash your system! But gives the " \
                          "best result"
        self.super_resolution_warning_display = QLabel(warning_message)
        self.super_resolution_warning_display.setWordWrap(True)
        self.super_resolution_warning_display.setStyleSheet("color: red;")

        self.super_resolution_warning_display.setHidden(True)

        font = QFont()
        font.setItalic(True)
        self.super_resolution_warning_display.setFont(font)

        # group the checkbox to make them mutually exclusive
        self.group_checkbox = QGroupBox("Method", self)

        # The enlargement method checkbox
        self.use_bilinear = QRadioButton("Bilinear", self.group_checkbox)
        self.use_cubic = QRadioButton("Cubic", self.group_checkbox)
        self.use_lanczos = QRadioButton("Lanczos", self.group_checkbox)
        self.use_super_resolution = QRadioButton("Super Resolution", self.group_checkbox)

        # set the default enlargement method
        self.use_bilinear.animateClick()

        # arrange them horizontally
        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.use_bilinear)
        layout_1.addWidget(self.use_cubic)
        layout_1.addWidget(self.use_lanczos)
        layout_1.addWidget(self.use_super_resolution)

        self.group_checkbox.setLayout(layout_1)

        # when they are clicked, they perform an action
        self.use_bilinear.clicked.connect(
            lambda: self.super_resolution_warning_display.setHidden(True))
        self.use_cubic.clicked.connect(
            lambda: self.super_resolution_warning_display.setHidden(True))
        self.use_lanczos.clicked.connect(
            lambda: self.super_resolution_warning_display.setHidden(True))
        self.use_super_resolution.clicked.connect(
            lambda: self.super_resolution_warning_display.setHidden(False))

        ######################################################

        self.enlargement_level = QComboBox()
        label = QLabel("Scale: ")
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.enlargement_level.addItems(['X2', 'X4', 'X8'])

        layout_2 = QHBoxLayout()

        layout_2.addWidget(label)
        layout_2.addWidget(self.enlargement_level)

        ########################################################

        self.initial_size_display = QLabel()
        self.final_size_display = QLabel()

        self.initial_size_label = QLabel("initial size:")
        self.final_size_label = QLabel("final size:")

        layout_3 = QGridLayout()
        layout_3.addWidget(self.initial_size_label, 0, 0)
        layout_3.addWidget(self.initial_size_display, 0, 1)
        layout_3.addWidget(self.final_size_label, 1, 0)
        layout_3.addWidget(self.final_size_display, 1, 1)

        ########################################################

        self.save_to_label = QLabel("Save to")
        self.save_to_display = QLineEdit()
        self.save_to_display.setDisabled(True)
        self.save_to_display.setStyleSheet("background-color: white")
        self.save_to_button = QPushButton("...")

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.save_to_label)
        layout_4.addWidget(self.save_to_display)
        layout_4.addWidget(self.save_to_button)

        ############################################################

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.super_resolution_warning_display)
        layout.addWidget(self.group_checkbox)
        layout.addLayout(layout_2)
        layout.addLayout(layout_3)
        layout.addLayout(layout_4)
        layout.addWidget(self.button_box)

        self.setLayout(layout)


class AboutInterface(QDialog):
    def __init__(self):
        super(AboutInterface, self).__init__()

        style_sheet = """
        background-color: #110f0d;
        color: white
        """
        self.setStyleSheet(style_sheet)

        img_path = "profile.jpg"
        pixmap = QPixmap(img_path)
        pixmap = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)

        text = "A Computer Engineering undergrad who finds great pleasure implementing Artificial Intelligence models," \
               " and what better way to do it, than in a desktop applications. Besides, building desktop applications" \
               " is cool." \
               "\n\n\nName: Samuel Nkopuruk E.\nEmail: samueleffiong80@gmail.com \nContacts: +2349035018948 " \
               "\n\nHave fun building models!"
        self.about_label = QLabel(text)
        self.about_label.setMaximumWidth(400)
        self.about_label.setWordWrap(True)

        # print(self.sizeHint())
        self.setFixedSize(500, 220)

        layout = QHBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.about_label, 2, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignJustify)

        self.setLayout(layout)
