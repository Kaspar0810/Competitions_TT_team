# manual_choice_fixed.py
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QGroupBox, QHeaderView, QScrollArea,
                             QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush

def manual_choice(sorted_sportsmen, count_exit, free_num, posevs_num, nums):
    """
    Функция ручной жеребьевки команд с автоматическим выбором команды
    """
    
    class ManualChoiceDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.sorted_sportsmen = sorted_sportsmen
            self.count_exit = count_exit
            self.free_num = free_num
            self.posevs_num = posevs_num
            self.nums = nums
            self.grid_size = self.get_grid_size()
            self.teams_count = len(sorted_sportsmen)
            
            # Словарь для хранения размещенных команд
            self.placed_teams = {}
            
            # Индекс текущей команды для посева
            self.current_team_index = 0
            
            # Список еще не размещенных команд
            self.remaining_teams = self.sorted_sportsmen.copy()
            
            # Свободные номера в сетке
            self.available_slots = self.get_available_slots()
            
            # Доступные номера для выбора на текущем этапе
            self.current_available_numbers = []
            
            # Результат
            self.result = None
            
            # Рассчитываем размеры в зависимости от типа сетки
            self.calculate_sizes_by_grid()
            
            self.init_ui()
            
            # Автоматически выбираем первую команду
            self.select_current_team()
            
        def get_grid_size(self):
            """Определение размера сетки на основе posevs_num"""
            max_num = 0
            for group in self.posevs_num:
                max_num = max(max_num, max(group))
            return max_num
            
        def calculate_sizes_by_grid(self):
            """Расчет размеров в зависимости от типа сетки (8, 16, 32)"""
            # Базовая высота строки
            if self.grid_size == 32:
                self.row_height = 18
                self.font_size = 8
                self.window_height = self.grid_size * self.row_height + 250
                self.table_max_height = self.grid_size * self.row_height + 100
                # self.window_height = 800
                # self.table_max_height = 700
                self.use_scroll = False
            elif self.grid_size == 16:
                self.row_height = 35
                self.font_size = 10
                # 16 * 35 = 560px, помещается без скролла
                self.window_height = self.grid_size * self.row_height + 250
                self.table_max_height = self.grid_size * self.row_height + 50
                self.use_scroll = False
            else:  # 8 команд
                self.row_height = 40
                self.font_size = 10
                # 8 * 40 = 320px, помещается без скролла
                self.window_height = self.grid_size * self.row_height + 250
                self.table_max_height = self.grid_size * self.row_height + 50
                self.use_scroll = False
                
            # Ширина окна
            self.window_width = 1300
            
            # Высота списка команд
            self.list_height = min(self.teams_count * self.row_height + 50, 500)
            
        def get_available_slots(self):
            """Получение списка доступных слотов в сетке"""
            all_slots = list(range(1, self.grid_size + 1))
            available = [slot for slot in all_slots if slot not in self.free_num]
            return available
            
        def get_current_available_numbers(self):
            """Получение доступных номеров для текущей команды"""
            if self.current_team_index >= len(self.sorted_sportsmen):
                return []
                
            # Определяем доступные номера в зависимости от этапа
            if self.current_team_index == 0:
                available = [1]
            elif self.current_team_index == 1:
                available = [8]
            elif self.current_team_index == 2 or self.current_team_index == 3:
                available = [4, 5]
            else:
                # Для сетки 8 команд
                if self.grid_size == 8:
                    available = [2, 3, 6, 7]
                # Для сетки 16 команд
                elif self.grid_size == 16:
                    available = [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16]
                    # Убираем уже занятые
                else:  # 32 команды
                    available = list(range(2, 33))
                    available.remove(8)
                    available.remove(4)
                    available.remove(5)
            
            # Фильтруем занятые номера
            available = [num for num in available if num in self.available_slots 
                        and num not in self.placed_teams]
            
            return available
            
        def select_current_team(self):
            """Автоматический выбор текущей команды"""
            if self.current_team_index < len(self.sorted_sportsmen):
                current_team = self.sorted_sportsmen[self.current_team_index]
                # Подсвечиваем текущую команду в списке
                for i in range(self.team_list.count()):
                    item = self.team_list.item(i)
                    team = item.data(Qt.UserRole)
                    if team and team[0] == current_team[0]:
                        self.team_list.setCurrentItem(item)
                        self.team_list.scrollToItem(item)
                        break
                
                self.status_label.setText(f"🎯 Очередь: {current_team[1]} (Рейтинг: {current_team[3]})")
                
        def update_current_available_numbers(self):
            """Обновление доступных номеров и отображения"""
            self.current_available_numbers = self.get_current_available_numbers()
            
            # Обновляем текст подсказки
            if self.current_team_index < len(self.sorted_sportsmen):
                team = self.sorted_sportsmen[self.current_team_index]
                if self.current_team_index == 0:
                    hint = f"1. Команда {team[1]} → номер 1"
                elif self.current_team_index == 1:
                    hint = f"2. Команда {team[1]} → номер 8"
                elif self.current_team_index == 2 or self.current_team_index == 3:
                    hint = f"{self.current_team_index + 1}. Команда {team[1]} → номера: {self.current_available_numbers}"
                else:
                    hint = f"{self.current_team_index + 1}. Команда {team[1]} → номера: {self.current_available_numbers}"
                
                if self.current_available_numbers:
                    self.current_seed_label.setText(hint)
                    self.current_seed_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    self.current_seed_label.setText(f"{hint}\n(нет доступных номеров!)")
                    self.current_seed_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.current_seed_label.setText("✅ Все команды размещены!")
                self.current_seed_label.setStyleSheet("color: blue; font-weight: bold;")
                
        def init_ui(self):
            self.setWindowTitle(f"Ручная жеребьевка (сетка {self.grid_size} | команд: {self.teams_count})")
            self.setGeometry(100, 100, self.window_width, self.window_height)
            self.setModal(True)
            
            # Центральный виджет
            central_widget = QWidget()
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(10)
            
            # ЛЕВАЯ ПАНЕЛЬ (список команд и управление)
            left_panel = self.create_left_panel()
            main_layout.addWidget(left_panel, 35)
            
            # ПРАВАЯ ПАНЕЛЬ (только таблица сетки)
            right_panel = self.create_right_panel()
            main_layout.addWidget(right_panel, 65)
            
            self.setLayout(main_layout)
            
            # Заполняем данные
            self.update_team_list()
            self.update_grid_table()
            self.update_current_available_numbers()
            
        def create_left_panel(self):
            """Создание левой панели"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(0, 0, 5, 0)
            layout.setSpacing(10)
            
            # Группа для списка команд
            team_group = QGroupBox(f"📋 СПИСОК КОМАНД (всего: {self.teams_count})")
            team_layout = QVBoxLayout(team_group)
            
            # Инструкция
            instruction = QLabel("✅ Команда выбирается автоматически\n👇 Кликните на ячейку в таблице для размещения")
            instruction.setStyleSheet("color: #0066cc; font-weight: bold; padding: 8px; background-color: #e7f3ff; border-radius: 5px;")
            instruction.setAlignment(Qt.AlignCenter)
            team_layout.addWidget(instruction)
            
            # Список команд
            if self.use_scroll and self.grid_size == 32:
            # if self.grid_size == 32:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QFrame.NoFrame)
                self.team_list = QListWidget()
                scroll.setWidget(self.team_list)
                team_layout.addWidget(scroll)
            else:
                self.team_list = QListWidget()
                team_layout.addWidget(self.team_list)
            
            self.team_list.setFont(QFont("Arial", self.font_size))
            self.team_list.setMinimumHeight(min(self.list_height, 500))
            
            team_layout.addWidget(self.team_list)
            layout.addWidget(team_group)
            
            # Группа с инструкцией по размещению
            info_group = QGroupBox("📌 ТЕКУЩАЯ КОМАНДА")
            info_layout = QVBoxLayout(info_group)
            
            self.current_seed_label = QLabel("Загрузка...")
            self.current_seed_label.setFont(QFont("Arial", 11))
            self.current_seed_label.setWordWrap(True)
            self.current_seed_label.setStyleSheet("padding: 8px; background-color: #f8f9fa; border-radius: 5px;")
            info_layout.addWidget(self.current_seed_label)
            
            layout.addWidget(info_group)
            
            # Группа с управлением
            control_group = QGroupBox("🎮 УПРАВЛЕНИЕ")
            control_layout = QVBoxLayout(control_group)
            
            # Статистика
            stats_frame = QFrame()
            stats_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 8px;")
            stats_layout = QVBoxLayout(stats_frame)
            
            # Прогресс
            progress_layout = QHBoxLayout()
            progress_layout.addWidget(QLabel("Прогресс:"))
            self.progress_label = QLabel("0%")
            self.progress_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
            progress_layout.addWidget(self.progress_label)
            progress_layout.addStretch()
            stats_layout.addLayout(progress_layout)
            
            # Счетчики
            counters_layout = QHBoxLayout()
            counters_layout.addWidget(QLabel("✅ Размещено:"))
            self.placed_count_label = QLabel("0")
            self.placed_count_label.setStyleSheet("color: #28a745; font-weight: bold;")
            counters_layout.addWidget(self.placed_count_label)
            counters_layout.addStretch()
            counters_layout.addWidget(QLabel("⏳ Осталось:"))
            self.remaining_count_label = QLabel(str(self.teams_count))
            self.remaining_count_label.setStyleSheet("color: #ff9800; font-weight: bold;")
            counters_layout.addWidget(self.remaining_count_label)
            stats_layout.addLayout(counters_layout)
            
            control_layout.addWidget(stats_frame)
            
            # Кнопки управления
            buttons_layout = QHBoxLayout()
            
            self.edit_button = QPushButton("✏️ Редактировать")
            self.edit_button.clicked.connect(self.edit_placement)
            self.edit_button.setStyleSheet("padding: 8px; font-size: 12px;")
            buttons_layout.addWidget(self.edit_button)
            
            self.reset_button = QPushButton("🔄 Сбросить")
            self.reset_button.clicked.connect(self.reset_draw)
            self.reset_button.setStyleSheet("padding: 8px; font-size: 12px;")
            buttons_layout.addWidget(self.reset_button)
            
            control_layout.addLayout(buttons_layout)
            
            # Кнопка завершения
            self.finish_button = QPushButton("✅ ЗАВЕРШИТЬ")
            self.finish_button.clicked.connect(self.finish_draw)
            self.finish_button.setStyleSheet("""
                background-color: #28a745; 
                color: white; 
                font-size: 13px; 
                padding: 10px; 
                border-radius: 5px;
                font-weight: bold;
            """)
            control_layout.addWidget(self.finish_button)
            
            # Кнопка отмены
            cancel_button = QPushButton("❌ Отменить")
            cancel_button.clicked.connect(self.reject)
            cancel_button.setStyleSheet("""
                background-color: #dc3545; 
                color: white; 
                font-size: 12px; 
                padding: 8px; 
                border-radius: 5px;
            """)
            control_layout.addWidget(cancel_button)
            
            layout.addWidget(control_group)
            
            # Статусная строка
            self.status_label = QLabel("✅ Готов к работе. Кликните на ячейку в таблице")
            self.status_label.setStyleSheet("color: #6c757d; padding: 8px; background-color: #f8f9fa; border-radius: 5px;")
            self.status_label.setWordWrap(True)
            layout.addWidget(self.status_label)
            
            return panel
            
        def create_right_panel(self):
            """Создание правой панели с таблицей сетки (прижата к верху)"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(5, 0, 0, 0)
            layout.setSpacing(0)
            layout.setAlignment(Qt.AlignTop)  # Прижимаем к верху
            
            # Группа для сетки
            grid_group = QGroupBox(f"🏆 СЕТКА ТУРНИРА (номера 1-{self.grid_size})")
            grid_layout = QVBoxLayout(grid_group)
            grid_layout.setAlignment(Qt.AlignTop)
            
            # Инструкция для таблицы
            instruction = QLabel("👇 КЛИКНИТЕ ПО ЯЧЕЙКЕ для размещения команды 👇")
            instruction.setStyleSheet("""
                color: #856404; 
                font-weight: bold; 
                background-color: #fff3cd; 
                padding: 8px; 
                border-radius: 5px;
                font-size: 12px;
            """)
            instruction.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(instruction)
            
            # Таблица
            if self.use_scroll and self.grid_size == 32:
            # if self.grid_size == 32:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QFrame.NoFrame)
                scroll.setAlignment(Qt.AlignTop)
                self.grid_table = QTableWidget()
                scroll.setWidget(self.grid_table)
                grid_layout.addWidget(scroll)
            else:
                self.grid_table = QTableWidget()
                grid_layout.addWidget(self.grid_table)
            
            # Настройка таблицы
            self.grid_table.setColumnCount(2)
            self.grid_table.setHorizontalHeaderLabels(["№ в сетке", "КОМАНДА"])
            self.grid_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.grid_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.grid_table.setSelectionBehavior(QTableWidget.SelectItems)
            self.grid_table.setSelectionMode(QTableWidget.SingleSelection)
            self.grid_table.cellClicked.connect(self.on_cell_clicked)
            
            # Устанавливаем высоту таблицы
            table_height = self.grid_size * self.row_height + 40
            self.grid_table.setMinimumHeight(table_height)
            if not self.use_scroll:
                self.grid_table.setMaximumHeight(table_height)
            
            # Прижимаем таблицу к верху
            self.grid_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            
            layout.addWidget(grid_group)
            
            # Добавляем распорку, чтобы заполнить оставшееся пространство
            layout.addStretch()
            
            return panel
            
        def update_team_list(self):
            """Обновление списка команд"""
            self.team_list.clear()
            
            for i, team in enumerate(self.remaining_teams):
                # Определяем очередь
                if i == 0:
                    queue = "→ 1"
                elif i == 1:
                    queue = "→ 8"
                elif i == 2 or i == 3:
                    queue = "→ 4/5"
                else:
                    queue = "→ 2,3,6,7"
                    
                is_current = (i == self.current_team_index)
                prefix = "👉 " if is_current else "   "
                
                # Формируем текст
                if self.grid_size == 32:
                    item_text = f"{prefix}{i+1}. {team[1]} | {team[2]} | {team[3]} {queue}"
                else:
                    item_text = f"{prefix}{i+1}. {team[1]} ({team[2]}) - {team[3]} {queue}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, team)
                
                font = QFont("Arial", self.font_size)
                item.setFont(font)
                
                if is_current:
                    item.setBackground(QColor(173, 216, 230))
                    font.setBold(True)
                    item.setFont(font)
                    
                self.team_list.addItem(item)
            
            # Обновляем статистику
            placed = len(self.placed_teams)
            self.placed_count_label.setText(str(placed))
            remaining = self.teams_count - placed
            self.remaining_count_label.setText(str(remaining))
            
            # Прогресс
            progress = int((placed / self.teams_count) * 100) if self.teams_count > 0 else 0
            self.progress_label.setText(f"{progress}%")
            
            if progress == 100:
                self.progress_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
            elif progress > 50:
                self.progress_label.setStyleSheet("color: #ff9800; font-weight: bold; font-size: 14px;")
            else:
                self.progress_label.setStyleSheet("color: #17a2b8; font-weight: bold; font-size: 14px;")
                
        def update_grid_table(self):
            """Обновление таблицы сетки"""
            self.grid_table.setRowCount(self.grid_size)
            
            for i in range(1, self.grid_size + 1):
                row = i - 1
                self.grid_table.setRowHeight(row, self.row_height)
                
                # Номер в сетке
                slot_item = QTableWidgetItem(str(i))
                slot_item.setTextAlignment(Qt.AlignCenter)
                slot_item.setFlags(slot_item.flags() & ~Qt.ItemIsEditable)
                
                # Определяем доступность
                is_available = (i in self.current_available_numbers)
                
                # Оформление
                if i in self.free_num:
                    slot_item.setBackground(QColor(200, 200, 200))
                    team_item = QTableWidgetItem("🚫 НЕТ КОМАНДЫ")
                    team_item.setBackground(QColor(200, 200, 200))
                elif i in self.placed_teams:
                    data = self.placed_teams[i]
                    if self.grid_size == 32:
                        text = f"✅ {data[0]} | {data[1]} | {data[2]}"
                    else:
                        text = f"✅ {data[0]} ({data[1]}) - {data[2]}"
                    team_item = QTableWidgetItem(text)
                    team_item.setBackground(QColor(144, 238, 144))
                    slot_item.setBackground(QColor(144, 238, 144))
                else:
                    if is_available:
                        team_item = QTableWidgetItem("🎯 КЛИКНИТЕ ДЛЯ РАЗМЕЩЕНИЯ!")
                        team_item.setBackground(QColor(255, 100, 100))
                        slot_item.setBackground(QColor(255, 100, 100))
                        team_item.setForeground(QBrush(QColor(255, 255, 255)))
                        slot_item.setForeground(QBrush(QColor(255, 255, 255)))
                    else:
                        team_item = QTableWidgetItem("⚪ СВОБОДНО")
                        team_item.setBackground(QColor(255, 255, 200))
                        slot_item.setBackground(QColor(255, 255, 200))
                
                team_item.setFlags(team_item.flags() & ~Qt.ItemIsEditable)
                self.grid_table.setItem(row, 0, slot_item)
                self.grid_table.setItem(row, 1, team_item)
                
        def on_cell_clicked(self, row, column):
            """Размещение команды по клику на ячейку"""
            if column not in [0, 1]:
                return
                
            slot = row + 1
            
            if self.current_team_index >= len(self.sorted_sportsmen):
                QMessageBox.information(self, "Информация", "Все команды уже размещены!")
                return
            
            current_team = self.sorted_sportsmen[self.current_team_index]
                
            if slot in self.free_num:
                QMessageBox.warning(self, "Ошибка", f"Номер {slot} - свободная позиция (нет команды в сетке)")
                return
                
            if slot in self.placed_teams:
                QMessageBox.warning(self, "Ошибка", f"Номер {slot} уже занят командой {self.placed_teams[slot][0]}")
                return
                
            if slot not in self.current_available_numbers:
                if self.current_team_index == 0:
                    msg = f"Первая команда ({current_team[1]}) должна быть на номер 1!"
                elif self.current_team_index == 1:
                    msg = f"Вторая команда ({current_team[1]}) должна быть на номер 8!"
                elif self.current_team_index <= 3:
                    msg = f"Команда {current_team[1]} должна быть на 4 или 5! Доступно: {self.current_available_numbers}"
                else:
                    msg = f"Команда {current_team[1]} должна быть на 2,3,6,7! Доступно: {self.current_available_numbers}"
                QMessageBox.warning(self, "Ошибка", msg)
                return
                
            # Размещаем команду
            self.placed_teams[slot] = [current_team[1], current_team[2], current_team[3], current_team[0]]
            self.remaining_teams.remove(current_team)
            self.current_team_index += 1
            
            self.update_current_available_numbers()
            self.update_team_list()
            self.update_grid_table()
            
            if self.current_team_index >= len(self.sorted_sportsmen):
                self.status_label.setText("🎉 ПОЗДРАВЛЯЮ! Жеребьевка завершена!")
                self.current_seed_label.setText("✅ Жеребьевка успешно завершена!")
                QMessageBox.information(self, "Успех", "Жеребьевка успешно завершена!")
            else:
                next_team = self.sorted_sportsmen[self.current_team_index]
                self.status_label.setText(f"✅ {current_team[1]} на {slot} место. Следующая: {next_team[1]}")
                # Автоматически выбираем следующую команду
                self.select_current_team()
                
        def edit_placement(self):
            """Редактирование размещения"""
            row = self.grid_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите ячейку с командой для редактирования")
                return
                
            slot = row + 1
            
            if slot in self.free_num:
                QMessageBox.warning(self, "Ошибка", "Это свободная позиция")
                return
                
            if slot not in self.placed_teams:
                QMessageBox.warning(self, "Ошибка", "Здесь нет команды")
                return
                
            data = self.placed_teams[slot]
            team_id = data[3]
            
            # Находим индекс команды
            idx = None
            for i, t in enumerate(self.sorted_sportsmen):
                if t[0] == team_id:
                    idx = i
                    break
                    
            if idx is None:
                QMessageBox.warning(self, "Ошибка", "Команда не найдена")
                return
                
            del self.placed_teams[slot]
            
            if idx < self.current_team_index:
                self.current_team_index = idx
                self.remaining_teams = self.sorted_sportsmen[idx:].copy()
                
            self.update_current_available_numbers()
            self.update_team_list()
            self.update_grid_table()
            self.status_label.setText(f"🔄 {data[0]} возвращена для переразмещения")
            self.select_current_team()
            
        def reset_draw(self):
            """Сброс жеребьевки"""
            reply = QMessageBox.question(self, "Подтверждение", 
                "Сбросить всю жеребьевку?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.placed_teams.clear()
                self.current_team_index = 0
                self.remaining_teams = self.sorted_sportsmen.copy()
                self.update_current_available_numbers()
                self.update_team_list()
                self.update_grid_table()
                self.status_label.setText("🔄 Жеребьевка сброшена")
                self.select_current_team()
                
        def finish_draw(self):
            """Завершение жеребьевки"""
            if self.current_team_index < len(self.sorted_sportsmen):
                remaining = len(self.sorted_sportsmen) - self.current_team_index
                reply = QMessageBox.question(self, "Подтверждение", 
                    f"Осталось {remaining} команд. Завершить?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                    
            result = {}
            for slot, data in self.placed_teams.items():
                result[slot] = [data[0], data[1], data[2]]
                
            self.result = result
            self.accept()
    
    # Запуск
    dialog = ManualChoiceDialog()
    result_code = dialog.exec_()
    return dialog.result if result_code == QDialog.Accepted else {}

# Тестирование
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Тест для разных размеров сетки
    test_size = 32  # Меняйте на 8, 16 или 32
    
    if test_size == 8:
        posevs = [[1, 8], [4, 5], [2, 3, 6, 7]]
        teams = []
        for i in range(1, 9):
            teams.append([i, f"Команда{i}", f"Город{i}", 100 - i])
    elif test_size == 16:
        posevs = [[1, 16], [8, 9], [4, 5, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15]]
        teams = []
        for i in range(1, 17):
            teams.append([i, f"Команда{i}", f"Город{i}", 100 - i])
    else:  # 32
        posevs = [[1, 32], [16, 17], [8, 9, 24, 25], [4, 5, 12, 13, 20, 21, 28, 29]]
        teams = []
        for i in range(1, 33):
            teams.append([i, f"Команда{i}", f"Город{i}", 100 - i])
    
    result = manual_choice(teams, 2, [], posevs, [1])
    
    if result:
        print("\n=== РЕЗУЛЬТАТЫ ЖЕРЕБЬЕВКИ ===")
        for slot in sorted(result.keys()):
            team = result[slot]
            print(f"Номер {slot:2d}: {team[0]:15s} ({team[1]:10s}) - Рейтинг: {team[2]}")