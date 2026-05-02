import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChoiceGroupManual(QDialog):  # Наследуемся от QDialog, а не от QMainWindow
    def __init__(self, athletes, parent=None):
        super().__init__(parent)
        self.athletes = athletes
        self.sorted_athletes = []
        self.groups = []
        self.num_groups = 4
        self.current_athlete_index = 0
        self.draw_order = []
        self.current_draw_step = 0
        self.group_tables = []
        self.group_headers = []
        self.result_data = None  # Для хранения результата
        self.initUI()
        self.load_athletes()
        self.init_groups()
        self.calculate_draw_order()
        self.setModal(True)  # Делаем окно модальным
        
    def initUI(self):
        self.setWindowTitle('Ручная жеребьевка спортсменов')
        self.setGeometry(100, 100, 1400, 800)
        
        # Основной layout
        main_layout = QVBoxLayout(self)  # Используем QVBoxLayout для QDialog
        
        # Верхняя часть с заголовком
        title_label = QLabel("Ручная жеребьевка спортсменов")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Основной горизонтальный layout для панелей
        content_layout = QHBoxLayout()
        
        # ========== ЛЕВАЯ ПАНЕЛЬ ==========
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.StyledPanel)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Информация о текущем спортсмене
        current_athlete_group = QGroupBox("Текущий спортсмен для посева")
        current_athlete_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        current_athlete_layout = QVBoxLayout(current_athlete_group)
        
        self.current_athlete_label = QLabel("Спортсмен: -")
        self.current_athlete_label.setStyleSheet("background-color: #ffe0b3; padding: 8px; font-size: 12px;")
        self.current_athlete_label.setWordWrap(True)
        current_athlete_layout.addWidget(self.current_athlete_label)
        
        left_layout.addWidget(current_athlete_group)
        
        # Информация о текущей группе
        current_group_group = QGroupBox("Текущая группа для посева")
        current_group_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        current_group_layout = QVBoxLayout(current_group_group)
        
        self.current_group_label = QLabel("Группа: -")
        self.current_group_label.setStyleSheet("background-color: #b3d9ff; padding: 8px; font-size: 12px;")
        current_group_layout.addWidget(self.current_group_label)
        
        left_layout.addWidget(current_group_group)
        
        # Список участников
        athletes_group = QGroupBox("Список участников (по рейтингу ↓)")
        athletes_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        athletes_layout = QVBoxLayout(athletes_group)
        
        self.athletes_table = QTableWidget()
        self.athletes_table.setColumnCount(4)
        self.athletes_table.setHorizontalHeaderLabels(["ID", "ФИО", "Рейтинг", "Регион"])
        self.athletes_table.horizontalHeader().setStretchLastSection(True)
        self.athletes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.athletes_table.setAlternatingRowColors(True)
        athletes_layout.addWidget(self.athletes_table)
        
        left_layout.addWidget(athletes_group)
        
        # Статистика и управление
        control_group = QGroupBox("Управление и статистика")
        control_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        control_layout = QVBoxLayout(control_group)
        
        # Статистика
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Всего спортсменов:"), 0, 0)
        self.total_label = QLabel("0")
        stats_layout.addWidget(self.total_label, 0, 1)
        stats_layout.addWidget(QLabel("Размещено:"), 1, 0)
        self.placed_label = QLabel("0")
        stats_layout.addWidget(self.placed_label, 1, 1)
        stats_layout.addWidget(QLabel("Осталось:"), 2, 0)
        self.remaining_label = QLabel("0")
        stats_layout.addWidget(self.remaining_label, 2, 1)
        control_layout.addLayout(stats_layout)
        
        # Кнопки управления
        btn_layout = QGridLayout()
        
        self.groups_combo = QComboBox()
        self.groups_combo.addItems([str(i) for i in range(2, 33)])
        self.groups_combo.setCurrentText(str(self.num_groups))
        self.groups_combo.currentTextChanged.connect(self.change_groups_count)
        btn_layout.addWidget(QLabel("Кол-во групп:"), 0, 0)
        btn_layout.addWidget(self.groups_combo, 0, 1)
        
        self.btn_reset = QPushButton("Сбросить жеребьевку")
        self.btn_reset.clicked.connect(self.reset_draw)
        btn_layout.addWidget(self.btn_reset, 1, 0, 1, 2)
        
        self.btn_auto = QPushButton("Авто-заполнение (1 номера)")
        self.btn_auto.clicked.connect(self.auto_fill_first)
        btn_layout.addWidget(self.btn_auto, 2, 0, 1, 2)
        
        self.btn_clear = QPushButton("Очистить все группы")
        self.btn_clear.clicked.connect(self.clear_all_groups)
        btn_layout.addWidget(self.btn_clear, 3, 0, 1, 2)
        
        self.btn_edit = QPushButton("Редактировать группы")
        self.btn_edit.clicked.connect(self.open_editor)
        self.btn_edit.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_edit, 4, 0, 1, 2)
        
        control_layout.addLayout(btn_layout)
        
        # Кнопки OK и Cancel
        dialog_buttons = QHBoxLayout()
        
        self.btn_result = QPushButton("Показать результат")
        self.btn_result.clicked.connect(self.show_results)
        self.btn_result.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        dialog_buttons.addWidget(self.btn_result)
        
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        dialog_buttons.addWidget(self.btn_ok)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        dialog_buttons.addWidget(self.btn_cancel)
        
        control_layout.addLayout(dialog_buttons)
        
        # Инструкция
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setReadOnly(True)
        info_text.setPlainText("Правила жеребьевки:\n"
                              "• Первые номера групп заполняются автоматически\n"
                              "• Клик по ячейке для посева текущего спортсмена\n"
                              "• Зеленые ячейки - можно сеять\n"
                              "• Желтые - совпадение региона, можно сеять с подтверждением\n"
                              "• Красные - совпадение региона и тренера\n"
                              "• Желтая подсветка группы - текущая для посева\n"
                              "• Двойной клик - редактирование ячейки")
        control_layout.addWidget(info_text)
        
        left_layout.addWidget(control_group)
        
        # ========== ЦЕНТРАЛЬНАЯ ПАНЕЛЬ (таблицы групп) ==========
        center_panel = QFrame()
        center_panel.setFrameStyle(QFrame.StyledPanel)
        center_layout = QVBoxLayout(center_panel)
        
        lbl_groups = QLabel("Жеребьевка групп")
        lbl_groups.setStyleSheet("font-weight: bold; font-size: 14px;")
        center_layout.addWidget(lbl_groups)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.groups_widget = QWidget()
        self.groups_layout = QGridLayout(self.groups_widget)
        scroll_area.setWidget(self.groups_widget)
        center_layout.addWidget(scroll_area)
        
        content_layout.addWidget(left_panel)
        content_layout.addWidget(center_panel, stretch=1)
        
        main_layout.addLayout(content_layout)
        
    def calculate_draw_order(self):
        """Расчет порядка посева групп (змейкой)"""
        self.draw_order = []
        for i in range(100):
            if i % 2 == 0:
                for g in range(self.num_groups):
                    self.draw_order.append(g)
            else:
                for g in range(self.num_groups - 1, -1, -1):
                    self.draw_order.append(g)
    
    def highlight_current_group(self):
        """Подсветка текущей группы для посева"""
        for header in self.group_headers:
            header.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; padding: 5px;")
        
        if self.current_draw_step < len(self.draw_order):
            current_group = self.draw_order[self.current_draw_step]
            if current_group < len(self.group_headers):
                self.group_headers[current_group].setStyleSheet(
                    "font-weight: bold; background-color: #FF9800; color: white; padding: 5px; border: 2px solid #FF5722;"
                )
                self.current_group_label.setText(f"Группа {current_group + 1}")
    
    def load_athletes(self):
        """Загрузка и сортировка спортсменов"""
        self.sorted_athletes = sorted(self.athletes, key=lambda x: x[2], reverse=True)
        self.update_athletes_table()
        self.update_current_athlete()
        
    def update_athletes_table(self):
        """Обновление таблицы участников"""
        remaining_athletes = self.sorted_athletes[self.current_athlete_index:]
        
        self.athletes_table.setRowCount(len(remaining_athletes))
        for row, athlete in enumerate(remaining_athletes):
            id_player, name, rating, region, coach = athlete
            self.athletes_table.setItem(row, 0, QTableWidgetItem(str(id_player)))
            self.athletes_table.setItem(row, 1, QTableWidgetItem(name))
            self.athletes_table.setItem(row, 2, QTableWidgetItem(str(rating)))
            self.athletes_table.setItem(row, 3, QTableWidgetItem(region))
        
        self.athletes_table.resizeColumnsToContents()
        
    def init_groups(self):
        """Инициализация таблиц групп"""
        for i in reversed(range(self.groups_layout.count())):
            widget = self.groups_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.group_tables.clear()
        self.group_headers.clear()
        
        cols_per_row = min(8, self.num_groups)
        
        for g in range(self.num_groups):
            group_frame = QFrame()
            group_frame.setFrameStyle(QFrame.Box)
            group_frame.setMinimumWidth(300)
            group_layout = QVBoxLayout(group_frame)
            
            header = QLabel(f"Группа {g+1}")
            header.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; padding: 5px;")
            header.setAlignment(Qt.AlignCenter)
            group_layout.addWidget(header)
            
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["№", "Участник (регион) тренер"])
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectItems)
            table.cellClicked.connect(self.on_cell_clicked)
            table.setEditTriggers(QTableWidget.DoubleClicked)
            table.itemDoubleClicked.connect(self.on_item_double_clicked)
            
            group_layout.addWidget(table)
            
            row = g // cols_per_row
            col = g % cols_per_row
            self.groups_layout.addWidget(group_frame, row, col)
            
            self.group_tables.append(table)
            self.group_headers.append(header)
        
        self.groups_layout.setSpacing(10)
        self.groups_layout.setContentsMargins(10, 10, 10, 10)
        
        if not self.groups:
            self.groups = [[] for _ in range(self.num_groups)]
        elif len(self.groups) != self.num_groups:
            if len(self.groups) > self.num_groups:
                self.groups = self.groups[:self.num_groups]
            else:
                while len(self.groups) < self.num_groups:
                    self.groups.append([])
        
        self.calculate_draw_order()
        self.current_draw_step = min(self.current_draw_step, len(self.draw_order) - 1)
        self.update_groups_display()
        self.highlight_current_group()
        
    def update_groups_display(self):
        """Обновление отображения всех групп"""
        for g_idx, table in enumerate(self.group_tables):
            max_rows = 0
            if g_idx < len(self.groups):
                max_rows = len(self.groups[g_idx])
            
            num_rows = max(10, max_rows + 2)
            table.setRowCount(num_rows)
            
            for row in range(num_rows):
                num_item = QTableWidgetItem(str(row + 1))
                num_item.setTextAlignment(Qt.AlignCenter)
                num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, num_item)
                
                if g_idx < len(self.groups) and row < len(self.groups[g_idx]) and self.groups[g_idx][row]:
                    athlete = self.groups[g_idx][row]
                    if athlete:
                        id_player, name, rating, region, coach = athlete
                        display_text = f"{name} ({region}) R:{rating} {coach}"
                        item = QTableWidgetItem(display_text)
                        item.setData(Qt.UserRole, id_player)
                        item.setFlags(item.flags() | Qt.ItemIsEditable)
                        table.setItem(row, 1, item)
                    else:
                        table.setItem(row, 1, QTableWidgetItem(""))
                else:
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(empty_item.flags() | Qt.ItemIsEditable)
                    table.setItem(row, 1, empty_item)
            
            table.resizeRowsToContents()
        
        self.update_stats()
        self.update_athletes_table()
        
    def update_stats(self):
        """Обновление статистики"""
        total = len(self.athletes)
        placed = sum(1 for group in self.groups for athlete in group if athlete)
        remaining = total - placed
        self.total_label.setText(str(total))
        self.placed_label.setText(str(placed))
        self.remaining_label.setText(str(remaining))
        self.update_current_athlete()
        
    def update_current_athlete(self):
        """Обновление отображения текущего спортсмена"""
        if self.current_athlete_index < len(self.sorted_athletes):
            athlete = self.sorted_athletes[self.current_athlete_index]
            id_player, name, rating, region, coach = athlete
            self.current_athlete_label.setText(f"Спортсмен: {name}\nРейтинг: {rating} | Регион: {region}\nТренер: {coach}")
            self.highlight_available_cells(athlete)
        else:
            self.current_athlete_label.setText("Жеребьевка завершена!")
            self.current_athlete_label.setStyleSheet("background-color: #90EE90; padding: 8px; font-size: 12px;")
    
    def check_conflicts(self, athlete, group_idx):
        """Проверка конфликтов: возвращает (region_conflict, coach_conflict)"""
        if group_idx >= len(self.groups):
            return False, False
            
        _, _, _, region, coach = athlete
        
        group_regions = [a[3] for a in self.groups[group_idx] if a]
        group_coaches = [a[4] for a in self.groups[group_idx] if a]
        
        region_conflict = region in group_regions
        coach_conflict = coach in group_coaches and region_conflict
        
        return region_conflict, coach_conflict
    
    def highlight_available_cells(self, athlete):
        """Подсветка доступных ячеек"""
        for table in self.group_tables:
            for row in range(table.rowCount()):
                num_item = table.item(row, 0)
                if num_item:
                    num_item.setBackground(QBrush(QColor(255, 255, 255)))
                    
        if not athlete:
            return
            
        for g_idx, table in enumerate(self.group_tables):
            for row in range(table.rowCount()):
                item = table.item(row, 1)
                if not item or not item.text():
                    region_conflict, coach_conflict = self.check_conflicts(athlete, g_idx)
                    
                    num_item = table.item(row, 0)
                    if num_item:
                        if coach_conflict:
                            num_item.setBackground(QBrush(QColor(255, 100, 100)))
                        elif region_conflict:
                            num_item.setBackground(QBrush(QColor(255, 255, 150)))
                        else:
                            num_item.setBackground(QBrush(QColor(144, 238, 144)))
    
    def can_place_athlete(self, athlete, group_idx, row):
        """Проверка возможности размещения (только занятость места)"""
        if group_idx >= len(self.groups):
            return False
            
        if row < len(self.groups[group_idx]) and self.groups[group_idx][row] is not None:
            return False
            
        return True
    
    def on_cell_clicked(self, row, col):
        """Обработка клика по ячейке"""
        if col != 1:
            return
            
        table = self.sender()
        if not table:
            return
            
        for g_idx, t in enumerate(self.group_tables):
            if t == table:
                if self.current_athlete_index >= len(self.sorted_athletes):
                    QMessageBox.information(self, "Информация", "Все спортсмены уже размещены!")
                    return
                
                current_athlete = self.sorted_athletes[self.current_athlete_index]
                
                if not self.can_place_athlete(current_athlete, g_idx, row):
                    QMessageBox.warning(self, "Ошибка", "Это место уже занято!")
                    return
                
                region_conflict, coach_conflict = self.check_conflicts(current_athlete, g_idx)
                
                if coach_conflict:
                    QMessageBox.warning(self, "Запрещено!",
                        f"Нельзя разместить {current_athlete[1]} в группу {g_idx + 1}!\n"
                        f"В группе уже есть спортсмен с таким же регионом ({current_athlete[3]}) и тренером ({current_athlete[4]}).")
                    return
                
                if region_conflict:
                    reply = QMessageBox.question(self, 'Конфликт регионов',
                        f'В группе {g_idx + 1} уже есть спортсмен из региона {current_athlete[3]}.\n'
                        f'Разместить {current_athlete[1]} в эту группу?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    
                    if reply == QMessageBox.No:
                        return
                
                while len(self.groups[g_idx]) <= row:
                    self.groups[g_idx].append(None)
                self.groups[g_idx][row] = current_athlete
                
                self.current_athlete_index += 1
                self.current_draw_step += 1
                
                self.update_groups_display()
                self.highlight_current_group()
                
                if self.current_athlete_index >= len(self.sorted_athletes):
                    QMessageBox.information(self, "Поздравляем!", "Жеребьевка успешно завершена!")
                break
    
    def on_item_double_clicked(self, item):
        """Редактирование ячейки"""
        if item.column() != 1:
            return
            
        table = item.tableWidget()
        row = item.row()
        
        for g_idx, t in enumerate(self.group_tables):
            if t == table:
                self.edit_cell(g_idx, row)
                break
    
    def edit_cell(self, group_idx, row):
        """Редактирование конкретной ячейки"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование ячейки")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        all_unplaced = self.sorted_athletes[self.current_athlete_index:]
        
        list_widget = QListWidget()
        
        current_athlete = None
        if group_idx < len(self.groups) and row < len(self.groups[group_idx]):
            current_athlete = self.groups[group_idx][row]
            if current_athlete:
                list_widget.addItem(f"--- Текущий: {current_athlete[1]} (Рейтинг: {current_athlete[2]}, Тренер: {current_athlete[4]}) ---")
        
        for athlete in all_unplaced:
            list_widget.addItem(f"{athlete[1]} (Рейтинг: {athlete[2]}, Регион: {athlete[3]}, Тренер: {athlete[4]})")
        
        list_widget.addItem("--- Очистить ячейку ---")
        
        layout.addWidget(QLabel("Выберите спортсмена для размещения:"))
        layout.addWidget(list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        
        def on_accept():
            selected = list_widget.currentRow()
            if selected >= 0:
                offset = 1 if current_athlete else 0
                
                if selected < len(all_unplaced) + offset:
                    athlete_idx = selected - offset
                    if athlete_idx >= 0 and athlete_idx < len(all_unplaced):
                        athlete = all_unplaced[athlete_idx]
                        
                        region_conflict, coach_conflict = self.check_conflicts(athlete, group_idx)
                        
                        if coach_conflict:
                            QMessageBox.warning(dialog, "Запрещено!",
                                f"Нельзя разместить {athlete[1]} в группу {group_idx + 1}!\n"
                                f"В группе уже есть спортсмен с таким же регионом и тренером.")
                            return
                        
                        if region_conflict:
                            reply = QMessageBox.question(dialog, 'Конфликт регионов',
                                f'В группе {group_idx + 1} уже есть спортсмен из региона {athlete[3]}.\n'
                                f'Все равно разместить?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            
                            if reply == QMessageBox.No:
                                return
                        
                        old_athlete = None
                        if group_idx < len(self.groups) and row < len(self.groups[group_idx]):
                            old_athlete = self.groups[group_idx][row]
                        
                        while len(self.groups[group_idx]) <= row:
                            self.groups[group_idx].append(None)
                        self.groups[group_idx][row] = athlete
                        
                        if athlete in self.sorted_athletes:
                            idx = self.sorted_athletes.index(athlete)
                            if idx >= self.current_athlete_index:
                                self.sorted_athletes.pop(idx)
                                if idx < self.current_athlete_index:
                                    self.current_athlete_index -= 1
                        
                        if old_athlete:
                            insert_pos = self.current_athlete_index
                            for i in range(self.current_athlete_index, len(self.sorted_athletes)):
                                if self.sorted_athletes[i][2] < old_athlete[2]:
                                    insert_pos = i
                                    break
                                insert_pos = i + 1
                            self.sorted_athletes.insert(insert_pos, old_athlete)
                        
                        self.update_groups_display()
                        self.update_current_athlete()
                        dialog.accept()
                elif selected == len(all_unplaced) + offset:
                    if group_idx < len(self.groups) and row < len(self.groups[group_idx]):
                        athlete = self.groups[group_idx][row]
                        self.groups[group_idx][row] = None
                        
                        if athlete:
                            insert_pos = self.current_athlete_index
                            for i in range(self.current_athlete_index, len(self.sorted_athletes)):
                                if self.sorted_athletes[i][2] < athlete[2]:
                                    insert_pos = i
                                    break
                                insert_pos = i + 1
                            self.sorted_athletes.insert(insert_pos, athlete)
                            self.update_groups_display()
                            self.update_current_athlete()
                            dialog.accept()
            else:
                QMessageBox.warning(dialog, "Ошибка", "Выберите спортсмена!")
        
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def open_editor(self):
        """Открыть редактор для обмена игроками между группами"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактор групп")
        dialog.setModal(True)
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        group_combos = []
        group_labels = []
        
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        for g_idx in range(self.num_groups):
            group_frame = QFrame()
            group_frame.setFrameStyle(QFrame.Box)
            group_layout = QVBoxLayout(group_frame)
            
            label = QLabel(f"Группа {g_idx + 1}")
            label.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; padding: 5px;")
            label.setAlignment(Qt.AlignCenter)
            group_layout.addWidget(label)
            
            combo = QComboBox()
            combo.addItem("--- Выберите спортсмена для перемещения ---")
            
            for row, athlete in enumerate(self.groups[g_idx]):
                if athlete:
                    combo.addItem(f"{row+1}. {athlete[1]} ({athlete[3]}) R:{athlete[2]} Тр:{athlete[4]}", (g_idx, row, athlete))
            
            group_layout.addWidget(combo)
            group_combos.append(combo)
            group_labels.append(label)
            
            scroll_layout.addWidget(group_frame, g_idx // 4, g_idx % 4)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        btn_layout = QHBoxLayout()
        
        btn_swap = QPushButton("Обменять выбранных")
        btn_swap.setStyleSheet("background-color: #2196F3; color: white;")
        btn_layout.addWidget(btn_swap)
        
        btn_move = QPushButton("Переместить")
        btn_move.setStyleSheet("background-color: #FF9800; color: white;")
        btn_layout.addWidget(btn_move)
        
        layout.addLayout(btn_layout)
        
        selected_athletes = []
        
        def on_combo_change(idx, group_idx):
            if idx > 0:
                athlete_data = group_combos[group_idx].itemData(idx)
                if athlete_data:
                    selected_athletes.append((group_idx, athlete_data))
                    group_combos[group_idx].setEnabled(False)
                    group_labels[group_idx].setStyleSheet("font-weight: bold; background-color: #FF9800; color: white; padding: 5px;")
        
        for g_idx, combo in enumerate(group_combos):
            combo.currentIndexChanged.connect(lambda idx, g=g_idx: on_combo_change(idx, g))
        
        def swap_athletes():
            if len(selected_athletes) == 2:
                g1, (row1, _, athlete1) = selected_athletes[0]
                g2, (row2, _, athlete2) = selected_athletes[1]
                
                self.groups[g1][row1], self.groups[g2][row2] = athlete2, athlete1
                
                dialog.accept()
                self.update_groups_display()
                QMessageBox.information(self, "Успех", "Спортсмены успешно обменяны!")
            else:
                QMessageBox.warning(self, "Ошибка", "Выберите ровно двух спортсменов для обмена!")
        
        def move_athlete():
            if len(selected_athletes) == 1:
                g1, (row1, _, athlete1) = selected_athletes[0]
                
                target_dialog = QDialog(dialog)
                target_dialog.setWindowTitle("Выберите цель")
                target_layout = QVBoxLayout(target_dialog)
                
                target_layout.addWidget(QLabel("Выберите группу:"))
                target_combo = QComboBox()
                target_combo.addItems([f"Группа {i+1}" for i in range(self.num_groups) if i != g1])
                target_layout.addWidget(target_combo)
                
                target_layout.addWidget(QLabel("Выберите строку:"))
                target_row_combo = QComboBox()
                target_row_combo.addItems([str(i+1) for i in range(20)])
                target_layout.addWidget(target_row_combo)
                
                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                target_layout.addWidget(buttons)
                
                def do_move():
                    target_group = target_combo.currentIndex()
                    if target_group >= g1:
                        target_group += 1
                    target_row = target_row_combo.currentIndex()
                    
                    if target_row < len(self.groups[target_group]) and self.groups[target_group][target_row] is not None:
                        QMessageBox.warning(self, "Ошибка", "Это место уже занято!")
                        return
                    
                    region_conflict, coach_conflict = self.check_conflicts(athlete1, target_group)
                    
                    if coach_conflict:
                        QMessageBox.warning(self, "Запрещено!",
                            f"Нельзя переместить {athlete1[1]} в группу {target_group + 1}!\n"
                            f"В группе уже есть спортсмен с таким же регионом и тренером.")
                        return
                    
                    if region_conflict:
                        reply = QMessageBox.question(target_dialog, 'Конфликт регионов',
                            f'В группе {target_group + 1} уже есть спортсмен из региона {athlete1[3]}.\n'
                            f'Все равно переместить?',
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        
                        if reply == QMessageBox.No:
                            return
                    
                    self.groups[g1][row1] = None
                    
                    while len(self.groups[target_group]) <= target_row:
                        self.groups[target_group].append(None)
                    self.groups[target_group][target_row] = athlete1
                    
                    target_dialog.accept()
                    dialog.accept()
                    self.update_groups_display()
                    QMessageBox.information(self, "Успех", "Спортсмен успешно перемещен!")
                
                buttons.accepted.connect(do_move)
                buttons.rejected.connect(target_dialog.reject)
                target_dialog.exec_()
            else:
                QMessageBox.warning(self, "Ошибка", "Выберите одного спортсмена для перемещения!")
        
        btn_swap.clicked.connect(swap_athletes)
        btn_move.clicked.connect(move_athlete)
        
        dialog.exec_()
    
    def change_groups_count(self, count):
        """Изменение количества групп"""
        self.num_groups = int(count)
        
        if len(self.groups) > self.num_groups:
            self.groups = self.groups[:self.num_groups]
        elif len(self.groups) < self.num_groups:
            while len(self.groups) < self.num_groups:
                self.groups.append([])
        
        self.init_groups()
        
        if self.current_athlete_index < len(self.sorted_athletes):
            self.highlight_available_cells(self.sorted_athletes[self.current_athlete_index])
    
    def reset_draw(self):
        """Полный сброс"""
        self.load_athletes()
        self.current_athlete_index = 0
        self.current_draw_step = 0
        self.groups = [[] for _ in range(self.num_groups)]
        self.calculate_draw_order()
        self.update_groups_display()
        self.highlight_current_group()
        self.current_athlete_label.setStyleSheet("background-color: #ffe0b3; padding: 8px; font-size: 12px;")
    
    def auto_fill_first(self):
        """Автоматическое заполнение первых номеров"""
        self.reset_draw()
        
        for i in range(min(self.num_groups, len(self.sorted_athletes))):
            self.groups[i] = [self.sorted_athletes[i]]
            self.current_athlete_index += 1
            self.current_draw_step += 1
        
        self.update_groups_display()
        self.highlight_current_group()
    
    def clear_all_groups(self):
        """Очистка всех групп"""
        all_athletes = []
        for group in self.groups:
            for athlete in group:
                if athlete:
                    all_athletes.append(athlete)
        
        self.groups = [[] for _ in range(self.num_groups)]
        self.sorted_athletes = sorted(all_athletes + self.sorted_athletes[self.current_athlete_index:], 
                                     key=lambda x: x[2], reverse=True)
        self.current_athlete_index = 0
        self.current_draw_step = 0
        self.update_groups_display()
        self.highlight_current_group()
        self.update_current_athlete()
    
    def show_results(self):
        """Показать результаты"""
        results = []
        for group_idx, group in enumerate(self.groups):
            for seed_num, athlete in enumerate(group, 1):
                if athlete:
                    results.append([
                        seed_num,
                        athlete[0],
                        athlete[1],
                        athlete[3]
                    ])
        
        results.sort(key=lambda x: x[0])
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Результаты жеребьевки")
        dialog.setModal(True)
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        result_table = QTableWidget()
        result_table.setColumnCount(4)
        result_table.setHorizontalHeaderLabels(["№ посева", "ID игрока", "ФИО", "Регион"])
        result_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            for col, value in enumerate(result):
                result_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        result_table.horizontalHeader().setStretchLastSection(True)
        result_table.resizeColumnsToContents()
        
        layout.addWidget(QLabel("Результаты жеребьевки:"))
        layout.addWidget(result_table)
        
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.exec_()
    
    def get_results(self):
        """Получить результаты жеребьевки для возврата в основную программу"""
        results = []
        for group_idx, group in enumerate(self.groups):
            gr = group_idx + 1
            for seed_num, athlete in enumerate(group, 1):
                if athlete:
                    results.append([
                        seed_num,
                        athlete[0],
                        athlete[1],
                        athlete[3],
                        gr
                    ])
        results.sort(key=lambda x: x[0])
        return results


def choice_group_manual(athletes, parent=None):
    """
    Функция для вызова ручной жеребьевки
    
    Args:
        athletes: список списков [id игрока, фамилия_имя, рейтинг, регион, тренер]
        parent: родительское окно
    
    Returns:
        list: список результатов [номер посева, id игрока, фио, регион] или None если отмена
    """
    dialog = ChoiceGroupManual(athletes, parent)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        return dialog.get_results()
    else:
        return None