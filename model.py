
import os
import cv2
import shutil
import numpy as np
from typing import Tuple, NewType, Callable
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QRunnable, QThreadPool
from cv2 import dnn_superres


class Worker(QRunnable):
    def __init__(self, func: Callable, params: dict):
        super(Worker, self).__init__()
        self.__func = func
        self.__params = params

    def run(self) -> None:

        self.__func(**self.__params)


# Define the type hint for the scale parameter
Width = NewType('Width', int)
Height = NewType('Height', int)
Multiplier = NewType('Multiplier', int)

Scale = Tuple[Width, Height]
Upscale = Tuple[Scale, Multiplier]


class _Thera:
    def __init__(self):
        print("Wake up Thera")
        self.__model_paths = {
            2: "models/lapSRN_x2.pb",
            4: "models/lapSRN_x4.pb",
            8: "models/lapSRN_x8.pb"
        }
        self.__sr = dnn_superres.DnnSuperResImpl_create()

    def bicula_scaling(self, image: np.ndarray,
                       upscale: Upscale, interpolation: str) -> np.ndarray:
        """Scale the image using the interpolation method specified by the
        interpolation param

        The available interpolation methods are Bilinear, Cubic and Lanczos
        :param image:
        :param upscale:
        :param interpolation:
         :return:
        """
        interpolation_dict = {
            'Bilinear': cv2.INTER_LINEAR,
            'Cubic': cv2.INTER_CUBIC,
            'Lanczos': cv2.INTER_LANCZOS4
        }
        image = cv2.resize(image, upscale[0],
                           interpolation=interpolation_dict[interpolation])
        return image

    def super_resolution(self, image: np.ndarray, upscale: Upscale) -> np.ndarray:
        multiplier = upscale[1]
        model_path = self.__model_paths[multiplier]
        self.__sr.readModel(model_path)
        self.__sr.setModel('lapsrn', 2)

        result = self.__sr.upsample(image)
        return result

    def save_enlarged_image(self, image: np.ndarray, filename) -> None:
        cv2.imwrite(filename, image)


class _ImageInterfaceControls:
    def __init__(self):
        # the variable enable the user to open new image in the same folder as the previous image
        # rather than always navigating from the app directory
        self.previous_path = None

        # this variable stores all the supported images in a folder to allow easy scrolling
        # through the images contained in that folder
        self.images_in_path = None

        # this variable stores the current image presently been viewed in the app
        self.current_img_in_view = None

    def display_image(self, view):
        image = QImage(self.current_img_in_view)

        # PyQt set the height or width value of a corrupted image to 0
        if image.height() <= 0 or image.width() <= 0:
            font = view.setup_font(font_family="Verdana", point_size=20, bold=True)
            view.image_container.setFont(font)
            view.image_container.setText("This image is corrupted")
            return

        screen_size = view.centralWidget().size()
        image = image.scaled(screen_size.width(), screen_size.height(),
                             aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                             transformMode=Qt.TransformationMode.SmoothTransformation)

        view.image_container.setPixmap(QPixmap.fromImage(image))
        view.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def open_image(self, view):
        """Allow the user to open any supported image from his directory to view
        """

        # set the supported format that the app will be able to display
        supported_format = ('bmp', 'jpeg', 'jpg', 'gif', 'png', 'svg', 'svgz', 'tif', 'webp')
        formats = [f"*.{ext}" for ext in supported_format]

        # if the user has selected an image from a folder, open the file dialog box
        # to that previous opened folder path
        if self.previous_path:
            filename, _ = QFileDialog().getOpenFileName(view, 'Select Image',
                                                        f'{self.previous_path}',
                                                        f'All images ({(" ".join(formats))});; '
                                                        "Jpeg (*.jpeg *.jpg);; GIF (*.gif);; "
                                                        "PNG (*.png);; SVG (*.svg *.svgz);; "
                                                        "TIF (*.tif);; "
                                                        "WEBP (*.webp);; Bitmap (*.bmp) ")

        # else open to the app home directory
        # TODO Challenge: Change this to start from the user desktop environment instead
        else:
            filename, _ = QFileDialog().getOpenFileName(view, 'Select Image', '.',
                                                        f'All images ({(" ".join(formats))});; '
                                                        "Jpeg (*.jpeg *.jpg);; GIF (*.gif);; "
                                                        "PNG (*.png);; SVG (*.svg *.svgz);; TIF (*.tif);; "
                                                        "WEBP (*.webp);; Bitmap (*.bmp) ")

        if filename:
            # save the absolute file path of the image
            self.current_img_in_view = filename

            self.display_image(view)

            # save th path of the folder containing the image
            self.previous_path = os.path.dirname(filename)

            # retrieve all the images contained in folder that is supported by the app
            self.images_in_path = [
                os.path.join(os.path.dirname(filename), img).replace('\\', '/')
                for img in os.listdir(os.path.dirname(filename))
                if img.split('.')[-1].lower() in supported_format
            ]
            # sort the images present in the folder, because most user give similar
            # names to related images
            self.images_in_path.sort()

            _, ext = os.path.splitext(self.current_img_in_view)

            # Identity the total number of images in the folder
            # and the position of the current image in relation to it
            self.total_image = len(self.images_in_path)
            self.current_image_index = self.images_in_path.index(self.current_img_in_view)

            # create an indicator showing the total number of images in the folder
            # and the current position in that folder
            view.setWindowTitle(f'{filename.split("/")[-1]}    '
                                               f'{self.current_image_index + 1} / {self.total_image}')

            view.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def rename_function(self, view):
        """Rename the current image been displayed in the app interface"""
        if self.current_img_in_view is not None:
            new_name, confirmation = QInputDialog().getText(view, "Rename file", "Enter new name")
            new_name = new_name.strip()

            # ensure the new_name is not empty
            if confirmation and new_name:
                # self-explanatory
                file_folder = os.path.dirname(self.current_img_in_view)
                file_ext = self.current_img_in_view.split(".")[-1]
                new_name = os.path.join(file_folder, new_name)
                new_name = "{}.{}".format(new_name.replace("\\", "/"), file_ext)
                os.rename(self.current_img_in_view, new_name)
                self.images_in_path[self.images_in_path.index(self.current_img_in_view)] = new_name
                self.current_img_in_view = new_name

                # sort the images alphabetically
                self.images_in_path.sort()

                self.current_image_index = self.images_in_path.index(self.current_img_in_view)
                view.setWindowTitle(f"{new_name.split('/')[-1]} - "
                                    f"{self.current_image_index + 1} / {self.total_image}")

    def navigate_image(self, direction, view):
        """Allows the app to scroll through the images contained in a folder
        in the forward or backward directions
        """

        # navigate through the images in the current image folder path
        if self.images_in_path:
            if direction == "down":  # backward direction
                try:
                    # keep moving backward through the list of images till you
                    # reach the image that is in the beginning file
                    self.current_img_in_view = self.images_in_path[
                        self.images_in_path.index(self.current_img_in_view) - 1
                    ]
                except IndexError:
                    # continue from the end of the file and keep going up to the beginning
                    self.current_img_in_view = self.images_in_path[-1]
            elif direction == "up":
                try:
                    # keep moving forward through the list of images till you
                    # reach the image that is in the end of the file
                    self.current_img_in_view = self.images_in_path[
                        self.images_in_path.index(self.current_img_in_view) + 1
                    ]
                except IndexError:
                    # continue from the beginning of the file and keep going down the list
                    self.current_img_in_view = self.images_in_path[0]

            self.total_image = len(self.images_in_path)
            self.current_image_index = self.images_in_path.index(self.current_img_in_view)

            self.display_image(view)

            view.setWindowTitle(f'{self.current_img_in_view.split("/")[-1]}    '
                                f'{self.current_image_index + 1} / {self.total_image}')

    def save_image(self, view):
        if self.current_img_in_view:
            filename = QFileDialog().getSaveFileName(view, "Save image as",
                                                     f"{self.previous_path}",
                                                     "Jpeg (*.jpeg *.jpg);; GIF (*.gif);; "
                                                     "PNG (*.png);; SVG (*.svg *.svgz);; "
                                                     "TIF (*.tif);; "
                                                     "WEBP (*.webp);; Bitmap (*.bmp) "
                                                     )
            filename = filename[0]
            if filename:
                filename_dirname = os.path.dirname(filename)
                current_dirname = os.path.dirname(self.current_img_in_view)

                if filename_dirname == current_dirname and filename not in self.images_in_path:
                    self.images_in_path.append(filename)
                    self.images_in_path.sort()

                    shutil.copy(self.current_img_in_view, filename)

                    self.total_image = len(self.images_in_path)
                    self.current_image_index = self.images_in_path.index(self.current_img_in_view)
                    view.setWindowTitle(f"{self.current_img_in_view.split('/')[-1]}"
                                        f"{self.current_image_index + 1} / {self.total_image}")

                elif filename_dirname != current_dirname:
                    shutil.copy(self.current_img_in_view, filename)


class _EnlargementDialogControls:
    def __init__(self):
        self.scale_converter = {'X2': 2, 'X4': 4, 'X8': 8}
        self.current_img_in_view = None

    def open_dialog(self, dialog):
        method = None
        filename = None

        self.image = QImage(self.current_img_in_view)
        self.display_projected_image_size(dialog)

        # dynamically connect a widget in the dialog to a signal, DARING
        dialog.enlargement_level.currentTextChanged.connect(
            lambda: self.display_projected_image_size(dialog))
        dialog.save_to_button.clicked.connect(
            lambda: self.open_save_to_dialog(dialog))

        if dialog.exec():
            filename = dialog.save_to_display.text().strip()
            self.new_filename = filename

            if dialog.use_bilinear.isChecked():
                method = dialog.use_bilinear.text()
            elif dialog.use_cubic.isChecked():
                method = dialog.use_cubic.text()
            elif dialog.use_lanczos.isChecked():
                method = dialog.use_lanczos.text()
            elif dialog.use_super_resolution.isChecked():
                method = dialog.use_super_resolution.text()

            # this line of code block is really not necessary
            # it is just to shut my code editor up about how the
            # variable might not be referenced
            if method is None:
                raise ValueError()

            scale_by = self.scale_converter[dialog.enlargement_level.currentText()]
            image_size = (self.image.width() * scale_by, self.image.height() * scale_by)
            upscale = (image_size, scale_by)

            dialog.parent.miscellaneous_event.enlargement_signal.emit(
                method, upscale, filename)

    def display_projected_image_size(self, dialog):
        # get the image size of the currently displayed image

        scale_converter = {'X2': 2, 'X4': 4, 'X8': 8}

        # ensure that the image not a corrupted image
        if self.image.width() <= 0 or self.image.height() <= 0:
            return
        else:
            scale = dialog.enlargement_level.currentText()
            new_width = self.image.width() * scale_converter[scale]
            new_height = self.image.height() * scale_converter[scale]

            final_size = f"{new_width} X {new_height}"
            initial_size = f"{self.image.width()} X {self.image.height()}"

            dialog.initial_size_display.setText(initial_size)
            dialog.final_size_display.setText(final_size)

    @staticmethod
    def open_save_to_dialog(dialog) -> str:
        filename = QFileDialog().getSaveFileName(dialog, "Save image as", ".",
                                                 "Jpeg (*.jpeg *.jpg);; GIF (*.gif);; "
                                                 "PNG (*.png);; SVG (*.svg *.svgz);; "
                                                 "TIF (*.tif);; "
                                                 "WEBP (*.webp);; Bitmap (*.bmp) "
                                                 )
        filename = filename[0]
        if filename:
            dialog.save_to_display.setText(filename)
            dialog.save_to_display.setDisabled(False)

            return filename


class Model:
    def __init__(self):
        self.__image_controls = _ImageInterfaceControls()
        self._enlargement_dialog_control = _EnlargementDialogControls()
        self.__thera = _Thera()

        # controls when to turn off the application
        self.turn_off = False

        self.__threadpool = QThreadPool()
        self.__threadpool.setMaxThreadCount(2)

    def activate_disable_menu_actions(self, view):
        if self.__image_controls.current_img_in_view is None:
            view.action_rename_image.setDisabled(True)
            view.action_save.setDisabled(True)
            view.action_image_enlargement.setDisabled(True)
        else:
            view.action_save.setDisabled(False)
            view.action_rename_image.setDisabled(False)
            view.action_image_enlargement.setDisabled(False)

    def open_image(self, view):
        self.__image_controls.open_image(view)
        self.activate_disable_menu_actions(view)

    def rename_image(self, view):
        self.__image_controls.rename_function(view)

    def navigate_image(self, direction, view):
        # self.__image_controls.navigate_image(direction, view)
        if self.__image_controls.current_img_in_view and direction.key() == Qt.Key.Key_Up:
            self.__image_controls.navigate_image("up", view)
        elif self.__image_controls.current_img_in_view and direction.key() == Qt.Key.Key_Down:
            self.__image_controls.navigate_image("down", view)

    def resize_image(self, view):
        if self.__image_controls.current_img_in_view is not None:
            self.__image_controls.display_image(view)

    def save_image(self, view):
        self.__image_controls.save_image(view)

    def exit_app(self, view, event):
        if not self.turn_off:
            confirmation = QMessageBox().warning(view, "Confirm Exit", "Are you sure you want to exit?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                 QMessageBox.StandardButton.No)

            if QMessageBox.StandardButton.Yes == confirmation:
                self.turn_off = True
                view.close()
            else:
                # pass
                try:
                    event.ignore()
                except AttributeError:
                    pass

    def open_enlargement_dialog_box(self, enlargement_dialog):
        # Save the file path of the image currently displayed as a variable
        # inside the EnlargeImageInterface class
        self._enlargement_dialog_control.current_img_in_view = self.__image_controls.current_img_in_view
        self._enlargement_dialog_control.open_dialog(enlargement_dialog)

    def __enlarge_image(self, view, interpolation=None, upscale: Upscale = None, filename=None):
        image = cv2.imread(self.__image_controls.current_img_in_view)
        view.status_bar.showMessage("Please wait, enlarging image...", 0)

        if interpolation != 'Super Resolution':
            image = self.__thera.bicula_scaling(image, upscale, interpolation)
        else:
            try:
                image = self.__thera.super_resolution(image, upscale)
            except cv2.error as e:
                print("Error: ", e.msg)

                # QMessageBox.warning(view, "Error", e.msg)

        self.__thera.save_enlarged_image(image, filename)
        view.status_bar.showMessage("Finished", 5000)

        view.miscellaneous_event.enlargement_finished.emit()

    def enlarge_image(self, view, interpolation=None, upscale=None, filename=None):
        params = {
            'view': view, 'interpolation': interpolation,
            'upscale': upscale, 'filename': filename
        }
        worker = Worker(self.__enlarge_image, params=params)
        self.__threadpool.start(worker)

    def end_of_enlargement_notification(self, view):
        text = f"Image has been successfully enlarged and save to:\n{self._enlargement_dialog_control.new_filename}"

        QMessageBox().information(view, "Success", text)

    def open_about_dialog(self, about_dialog):
        self.about_dialog = about_dialog
        self.about_dialog.show()
