# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 16:33:27 2023

@author: kaiar
"""

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from PyQt5.QtGui import QPainter, QIcon, QBrush, QPalette, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QLocale, QSize, QRect, QPoint, QTimer, pyqtSlot
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QAbstractSpinBox,
    QDoubleSpinBox,
    QSlider,
    QStyle,
    QFormLayout,
    QApplication,
    QFrame,
    QFileDialog,
    QPushButton,
    QMainWindow,
    QStyleOptionSlider,
    QMessageBox,
    QDialog
)

class DragAndDropLabelwithButton(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, text):
        super(DragAndDropLabelwithButton, self).__init__()
        self.setObjectName("DragAndDropLabelwithButton")
        self.file = text
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.file_path = None
        self.setStyleSheet(
            "QFrame#DragAndDropLabelwithButton {border: 2px dashed #aaa; border-radius: 10px}"
        )
        self.label = QLabel("Drop " + self.file + " here\nor")
        self.label.setAlignment(Qt.AlignCenter)
        button = QPushButton("Select File")
        button.clicked.connect(self.chooseFile)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(button)
        layout.addStretch()
        self.setLayout(layout)

    def chooseFile(self):
        options = QFileDialog.Options()
        self.file_path = QFileDialog.getExistingDirectory(
            self,
            "Choose your Beamtimefolder",
            "",
            #"All Files (*);;Text Files (*.txt)",
            options=options,
        )
        if self.file_path:
            self.fileDropped.emit(self.file_path)
 

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px dashed #00f; border-radius: 10px}"
            )
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        if not self.file_path:
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px dashed #aaa; border-radius: 10px}"
            )
        else:
            self.setStyleSheet(
                "QFrame#DragAndDropLabelwithButton {border: 2px solid green; border-radius: 10px}"
            )

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.file_path = str(url.toLocalFile())
            self.fileDropped.emit(self.file_path)
        event.accept()

class QtWaitingSpinner(QWidget):
    mColor = QColor(Qt.gray)
    mRoundness = 100.0
    mMinimumTrailOpacity = 31.4159265358979323846
    mTrailFadePercentage = 50.0
    mRevolutionsPerSecond = 1.57079632679489661923
    mNumberOfLines = 20
    mLineLength = 10
    mLineWidth = 2
    mInnerRadius = 20
    mCurrentCounter = 0
    mIsSpinning = False

    def __init__(self, centerOnParent=True, disableParentWhenSpinning=True, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.mCenterOnParent = centerOnParent
        self.mDisableParentWhenSpinning = disableParentWhenSpinning
        self.initialize()

    def initialize(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()

    @pyqtSlot()
    def rotate(self):
        self.mCurrentCounter += 1
        if self.mCurrentCounter > self.numberOfLines():
            self.mCurrentCounter = 0
        self.update()

    def updateSize(self):
        size = (self.mInnerRadius + self.mLineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self.timer.setInterval(1000 / (self.mNumberOfLines * self.mRevolutionsPerSecond))

    def updatePosition(self):
        if self.parentWidget() and self.mCenterOnParent:
            self.move(self.parentWidget().width() / 2 - self.width() / 2,
                      self.parentWidget().height() / 2 - self.height() / 2)

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, color):
        if countDistance == 0:
            return color

        minAlphaF = minOpacity / 100.0

        distanceThreshold = ceil((totalNrOfLines - 1) * trailFadePerc / 100.0)
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)

        else:
            alphaDiff = self.mColor.alphaF() - minAlphaF
            gradient = alphaDiff / distanceThreshold + 1.0
            resultAlpha = color.alphaF() - gradient * countDistance
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color

    def paintEvent(self, event):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.mCurrentCounter > self.mNumberOfLines:
            self.mCurrentCounter = 0
        painter.setPen(Qt.NoPen)

        for i in range(self.mNumberOfLines):
            painter.save()
            painter.translate(self.mInnerRadius + self.mLineLength,
                              self.mInnerRadius + self.mLineLength)
            rotateAngle = 360.0 * i / self.mNumberOfLines
            painter.rotate(rotateAngle)
            painter.translate(self.mInnerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(i, self.mCurrentCounter,
                                                         self.mNumberOfLines)
            color = self.currentLineColor(distance, self.mNumberOfLines,
                                          self.mTrailFadePercentage, self.mMinimumTrailOpacity, self.mColor)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(0, -self.mLineWidth // 2, self.mLineLength, self.mLineLength),
                                    self.mRoundness, Qt.RelativeSize)
            painter.restore()

    def start(self):
        self.updatePosition()
        self.mIsSpinning = True
        self.show()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self.timer.isActive():
            self.timer.start()
            self.mCurrentCounter = 0

    def stop(self):
        self.mIsSpinning = False
        self.hide()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self.timer.isActive():
            self.timer.stop()
            self.mCurrentCounter = 0

    def setNumberOfLines(self, lines):
        self.mNumberOfLines = lines
        self.updateTimer()

    def setLineLength(self, length):
        self.mLineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self.mLineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self.mInnerRadius = radius
        self.updateSize()

    def color(self):
        return self.mColor

    def roundness(self):
        return self.mRoundness

    def minimumTrailOpacity(self):
        return self.mMinimumTrailOpacity

    def trailFadePercentage(self):
        return self.mTrailFadePercentage

    def revolutionsPersSecond(self):
        return self.mRevolutionsPerSecond

    def numberOfLines(self):
        return self.mNumberOfLines

    def lineLength(self):
        return self.mLineLength

    def lineWidth(self):
        return self.mLineWidth

    def innerRadius(self):
        return self.mInnerRadius

    def isSpinning(self):
        return self.mIsSpinning

    def setRoundness(self, roundness):
        self.mRoundness = min(0.0, max(100, roundness))

    def setColor(self, color):
        self.mColor = color

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self.mRevolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self.mTrailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self.mMinimumTrailOpacity = minimumTrailOpacity