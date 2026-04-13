import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QGroupBox, QComboBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
# import main

def choice_net_manual(sorted_sportsmen, count_exit, free_num, posevs_num, nums):
    """
    Функция ручной жеребьевки команд
    
    sorted_sportsmen: список списков [id_team, team_name, team_region, r_sum]
    count_exit: число выходящих из группы 1 или 2
    free_num: номера в сетке где не будет команды
    posevs_num: список списков [[1, 8], [4,5], [2,3,6,7]] это для сетки на 8 команд
    nums: места, занятые в группе [1]
    
    возвращает: словарь {номер_в_сетке: [название_команды, регион, r_sum]}
    """
    
    class ManualChoiceWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.sorted_sportsmen = sorted_sportsmen
            self.count_exit = count_exit
            self.free_num = free_num
            self.posevs_num = posevs_num
            self.nums = nums
            self.grid_size = self.get_grid_size()
            
            # Словарь для хранения размещенных команд
            self.placed_teams = {}  # {номер_в_сетке: [название, регион, рейтинг, id]}
            
            # Индекс текущей команды для посева (0, 1, 2, 3, 4...)
            self.current_team_index = 0
            
            # Список еще не размещенных команд
            self.remaining_teams = self.sorted_sportsmen.copy()
            
            # Свободные номера в сетке
            self.available_slots = self.get_available_slots()
            
            # Доступные номера для выбора на текущем этапе
            self.current_available_numbers = []
            
            self.init_ui()
            
        def get_grid_size(self):
            """Определение размера сетки на основе posevs_num"""
            max_num = 0
            max_num = self.posevs_num[0]
            # for group in self.posevs_num:
            #     max_num = max(max_num, max(group))
            return max_num
            
        def get_available_slots(self):
            """Получение списка доступных слотов в сетке"""
            all_slots = list(range(1, self.grid_size + 1))
            available = [slot for slot in all_slots if slot not in self.free_num]
            return available
            
        def get_current_available_numbers(self):
            """Получение доступных номеров для текущей команды"""
            if self.current_team_index >= len(self.sorted_sportsmen):
                return []
                
            # Определяем, на каком этапе посева находимся
            if self.current_team_index == 0:
                # 1-я команда - только номер 1
                available = [1]
            elif self.current_team_index == 1:
                # 2-я команда - только номер 8
                available = [8]
            elif self.current_team_index == 2 or self.current_team_index == 3:
                # 3-я и 4-я команды - номера 4 или 5
                available = [4, 5]
            else:
                # Остальные команды - номера 2, 3, 6, 7
                available = [2, 3, 6, 7]
            
            # Фильтруем уже занятые номера и свободные номера
            available = [num for num in available if num in self.available_slots 
                        and num not in self.placed_teams]
            
            return available
            
        def update_current_available_numbers(self):
            """Обновление доступных номеров и отображения"""
            self.current_available_numbers = self.get_current_available_numbers()
            
            # Обновляем текст подсказки
            if self.current_team_index < len(self.sorted_sportsmen):
                team = self.sorted_sportsmen[self.current_team_index]
                if self.current_team_index == 0:
                    hint = f"Команда {team[1]} должна быть размещена на номер 1"
                elif self.current_team_index == 1:
                    hint = f"Команда {team[1]} должна быть размещена на номер 8"
                elif self.current_team_index == 2 or self.current_team_index == 3:
                    hint = f"Команда {team[1]} может быть размещена на номера: {self.current_available_numbers}"
                else:
                    hint = f"Команда {team[1]} может быть размещена на номера: {self.current_available_numbers}"
                
                if self.current_available_numbers:
                    self.current_seed_label.setText(hint)
                else:
                    self.current_seed_label.setText(f"{hint}\n(нет доступных номеров!)")
            else:
                self.current_seed_label.setText("Все команды размещены!")
                
        def init_ui(self):
            self.setWindowTitle("Ручная жеребьевка команд")
            self.setGeometry(100, 100, 1200, 600)
            
            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Основной горизонтальный layout
            main_layout = QHBoxLayout(central_widget)
            
            # Левая панель - список команд
            left_panel = self.create_left_panel()
            main_layout.addWidget(left_panel, 1)
            
            # Правая панель - сетка и управление
            right_panel = self.create_right_panel()
            main_layout.addWidget(right_panel, 2)
            
            # Заполняем список команд
            self.update_team_list()
            
            # Обновляем таблицу сетки
            self.update_grid_table()
            
            # Обновляем доступные номера
            self.update_current_available_numbers()
            
        def create_left_panel(self):
            """Создание левой панели со списком команд"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Группа для списка команд
            group_box = QGroupBox("Список команд (по убыванию рейтинга)")
            group_layout = QVBoxLayout(group_box)
            
            # Список команд
            self.team_list = QListWidget()
            self.team_list.setFont(QFont("Arial", 10))
            self.team_list.itemClicked.connect(self.on_team_selected)
            group_layout.addWidget(self.team_list)
            
            layout.addWidget(group_box)
            
            # Текущий этап посева
            current_seed_group = QGroupBox("Текущая команда для посева")
            seed_layout = QVBoxLayout(current_seed_group)
            self.current_seed_label = QLabel("Загрузка...")
            self.current_seed_label.setFont(QFont("Arial", 11))
            self.current_seed_label.setStyleSheet("color: blue;")
            self.current_seed_label.setWordWrap(True)
            seed_layout.addWidget(self.current_seed_label)
            layout.addWidget(current_seed_group)
            
            return panel
            
        def create_right_panel(self):
            """Создание правой панели с сеткой и управлением"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            
            # Таблица сетки
            grid_group = QGroupBox(f"Сетка турнира (номера 1-{self.grid_size})")
            grid_layout = QVBoxLayout(grid_group)
            
            self.grid_table = QTableWidget()
            self.grid_table.setColumnCount(2)
            self.grid_table.setHorizontalHeaderLabels(["Номер в сетке", "Команда"])
            
            # Настройка таблицы
            self.grid_table.setColumnWidth(0, 100)
            self.grid_table.setColumnWidth(1, 350)
            
            grid_layout.addWidget(self.grid_table)
            layout.addWidget(grid_group)
            
            # Панель управления
            control_group = QGroupBox("Управление жеребьевкой")
            control_layout = QVBoxLayout(control_group)
            
            # Выбор номера для размещения
            slot_layout = QHBoxLayout()
            slot_layout.addWidget(QLabel("Номер в сетке:"))
            self.slot_input = QLineEdit()
            self.slot_input.setPlaceholderText(f"Введите номер от 1 до {self.grid_size}")
            slot_layout.addWidget(self.slot_input)
            control_layout.addLayout(slot_layout)
            
            # Кнопки управления
            buttons_layout = QHBoxLayout()
            
            self.place_button = QPushButton("Разместить команду")
            self.place_button.clicked.connect(self.place_team)
            buttons_layout.addWidget(self.place_button)
            
            self.edit_button = QPushButton("Редактировать")
            self.edit_button.clicked.connect(self.edit_placement)
            buttons_layout.addWidget(self.edit_button)
            
            self.reset_button = QPushButton("Сбросить жеребьевку")
            self.reset_button.clicked.connect(self.reset_draw)
            buttons_layout.addWidget(self.reset_button)
            
            control_layout.addLayout(buttons_layout)
            
            # Кнопка завершения
            self.finish_button = QPushButton("Завершить жеребьевку")
            self.finish_button.clicked.connect(self.finish_draw)
            self.finish_button.setStyleSheet("background-color: green; color: white; font-size: 14px;")
            control_layout.addWidget(self.finish_button)
            
            layout.addWidget(control_group)
            
            # Статусная строка
            self.status_label = QLabel("Готов к работе")
            self.status_label.setStyleSheet("color: gray;")
            layout.addWidget(self.status_label)
            
            return panel
            
        def update_team_list(self):
            """Обновление списка команд"""
            self.team_list.clear()
            for i, team in enumerate(self.remaining_teams):
                # Определяем номер очереди для каждой команды
                if i == 0:
                    queue_info = " (очередь: номер 1)"
                elif i == 1:
                    queue_info = " (очередь: номер 8)"
                elif i == 2 or i == 3:
                    queue_info = " (очередь: номер 4 или 5)"
                else:
                    queue_info = " (очередь: номер 2,3,6 или 7)"
                    
                item_text = f"{team[1]} ({team[2]}) - Рейтинг: {team[3]}{queue_info}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, team)
                
                # Подсвечиваем текущую команду
                if i == self.current_team_index:
                    item.setBackground(QColor(173, 216, 230))  # Светло-голубой
                    font = QFont("Arial", 10, QFont.Bold)
                    item.setFont(font)
                    
                self.team_list.addItem(item)
                
        def on_team_selected(self, item):
            """Обработка выбора команды из списка"""
            team = item.data(Qt.UserRole)
            self.selected_team = team
            self.status_label.setText(f"Выбрана команда: {team[1]}")
            
        def update_grid_table(self):
            """Обновление таблицы сетки"""
            self.grid_table.setRowCount(self.grid_size)
            
            for i in range(1, self.grid_size + 1):
                row = i - 1
                
                # Номер в сетке
                slot_item = QTableWidgetItem(str(i))
                slot_item.setTextAlignment(Qt.AlignCenter)
                
                # Если номер свободен
                if i in self.free_num:
                    slot_item.setBackground(QColor(200, 200, 200))
                    team_item = QTableWidgetItem("СВОБОДНО (нет команды)")
                    team_item.setBackground(QColor(200, 200, 200))
                # Если номер занят командой
                elif i in self.placed_teams:
                    team_data = self.placed_teams[i]
                    team_item = QTableWidgetItem(f"{team_data[0]} ({team_data[1]}) - Рейтинг: {team_data[2]}")
                    team_item.setBackground(QColor(144, 238, 144))  # Светло-зеленый
                    slot_item.setBackground(QColor(144, 238, 144))
                # Если номер свободен для размещения
                else:
                    # Подсвечиваем доступные для текущей команды номера
                    if i in self.current_available_numbers:
                        team_item = QTableWidgetItem("СВОБОДНО (доступно для текущей команды)")
                        team_item.setBackground(QColor(255, 255, 100))  # Желтый
                        slot_item.setBackground(QColor(255, 255, 100))
                    else:
                        team_item = QTableWidgetItem("СВОБОДНО")
                        team_item.setBackground(QColor(255, 255, 200))
                        slot_item.setBackground(QColor(255, 255, 200))
                    
                self.grid_table.setItem(row, 0, slot_item)
                self.grid_table.setItem(row, 1, team_item)
                
            # Автоматическое изменение размера строк
            self.grid_table.resizeRowsToContents()
            
        def place_team(self):
            """Размещение выбранной команды в сетке"""
            # Проверяем, есть ли еще команды для размещения
            if self.current_team_index >= len(self.sorted_sportsmen):
                QMessageBox.information(self, "Информация", "Все команды уже размещены!")
                return
                
            # Получаем текущую команду
            current_team = self.sorted_sportsmen[self.current_team_index]
            
            # Проверяем, что выбрана правильная команда
            if hasattr(self, 'selected_team'):
                if self.selected_team[0] != current_team[0]:
                    QMessageBox.warning(self, "Ошибка", 
                                      f"Сейчас должна быть размещена команда: {current_team[1]}\n"
                                      f"Пожалуйста, выберите правильную команду из списка!")
                    return
            else:
                QMessageBox.warning(self, "Ошибка", 
                                  f"Пожалуйста, выберите команду {current_team[1]} из списка!")
                return
                
            try:
                slot_num = int(self.slot_input.text())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный номер!")
                return
                
            # Проверка валидности номера
            if slot_num < 1 or slot_num > self.grid_size:
                QMessageBox.warning(self, "Ошибка", f"Номер должен быть в диапазоне от 1 до {self.grid_size}!")
                return
                
            # Проверка, что номер не свободен
            if slot_num in self.free_num:
                QMessageBox.warning(self, "Ошибка", f"Номер {slot_num} свободен (нет команды в сетке)!")
                return
                
            # Проверка, что номер не занят
            if slot_num in self.placed_teams:
                QMessageBox.warning(self, "Ошибка", f"Номер {slot_num} уже занят командой {self.placed_teams[slot_num][0]}!")
                return
                
            # Проверка, что номер доступен для текущей команды
            if slot_num not in self.current_available_numbers:
                if self.current_team_index == 0:
                    QMessageBox.warning(self, "Ошибка", f"Первая команда должна быть размещена ТОЛЬКО на номер 1!")
                elif self.current_team_index == 1:
                    QMessageBox.warning(self, "Ошибка", f"Вторая команда должна быть размещена ТОЛЬКО на номер 8!")
                elif self.current_team_index == 2 or self.current_team_index == 3:
                    QMessageBox.warning(self, "Ошибка", f"Команда {self.current_team_index + 1} должна быть размещена на номера 4 или 5!")
                else:
                    QMessageBox.warning(self, "Ошибка", f"Команда {self.current_team_index + 1} должна быть размещена на номера 2, 3, 6 или 7!")
                return
                
            # Размещение команды
            team = self.selected_team
            self.placed_teams[slot_num] = [team[1], team[2], team[3], team[0]]
            
            # Удаление команды из списка оставшихся
            self.remaining_teams.remove(team)
            
            # Переход к следующей команде
            self.current_team_index += 1
            
            # Очистка выбора
            if hasattr(self, 'selected_team'):
                delattr(self, 'selected_team')
            self.slot_input.clear()
            
            # Обновление доступных номеров для следующей команды
            self.update_current_available_numbers()
            
            # Обновление интерфейса
            self.update_team_list()
            self.update_grid_table()
            
            # Проверка, завершена ли жеребьевка
            if self.current_team_index >= len(self.sorted_sportsmen):
                self.status_label.setText(f"Жеребьевка завершена! Все команды размещены.")
                QMessageBox.information(self, "Поздравляем", "Жеребьевка успешно завершена!")
            else:
                next_team = self.sorted_sportsmen[self.current_team_index]
                self.status_label.setText(f"Команда {team[1]} размещена на позиции {slot_num}. Следующая команда: {next_team[1]}")
            
        def edit_placement(self):
            """Редактирование размещения"""
            current_row = self.grid_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите ячейку с командой для редактирования!")
                return
                
            slot_num = current_row + 1
            
            if slot_num in self.free_num:
                QMessageBox.warning(self, "Ошибка", "Этот номер свободен, здесь нет команды для редактирования!")
                return
                
            if slot_num not in self.placed_teams:
                QMessageBox.warning(self, "Ошибка", "На этом номере нет размещенной команды!")
                return
                
            # Получаем данные команды
            team_data = self.placed_teams[slot_num]
            
            # Находим индекс этой команды в исходном списке
            team_id = team_data[3]
            original_index = None
            for i, team in enumerate(self.sorted_sportsmen):
                if team[0] == team_id:
                    original_index = i
                    break
                    
            if original_index is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти команду в исходном списке!")
                return
                
            # Удаляем из размещенных
            del self.placed_teams[slot_num]
            
            # Обновляем текущий индекс, если редактируем команду, которая была размещена позже
            if original_index < self.current_team_index:
                # Сдвигаем все последующие команды
                self.current_team_index = original_index
                # Восстанавливаем список оставшихся команд
                self.remaining_teams = self.sorted_sportsmen[original_index:].copy()
                
            # Сортируем оставшиеся команды по рейтингу
            self.remaining_teams.sort(key=lambda x: x[3], reverse=True)
            
            # Обновляем доступные номера
            self.update_current_available_numbers()
            
            # Очищаем выбор
            if hasattr(self, 'selected_team'):
                delattr(self, 'selected_team')
                
            self.slot_input.clear()
            self.update_team_list()
            self.update_grid_table()
            self.status_label.setText(f"Команда {team_data[0]} возвращена в список для переразмещения")
            
        def reset_draw(self):
            """Сброс всей жеребьевки"""
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Вы уверены, что хотите сбросить всю жеребьевку?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Сбрасываем все данные
                self.placed_teams.clear()
                self.current_team_index = 0
                self.remaining_teams = self.sorted_sportsmen.copy()
                
                # Очищаем выбор
                if hasattr(self, 'selected_team'):
                    delattr(self, 'selected_team')
                    
                self.slot_input.clear()
                
                # Обновляем доступные номера
                self.update_current_available_numbers()
                
                # Обновляем интерфейс
                self.update_team_list()
                self.update_grid_table()
                self.status_label.setText("Жеребьевка сброшена. Начните заново.")
                
        def finish_draw(self):
            """Завершение жеребьевки"""
            # Проверяем, все ли команды размещены
            if self.current_team_index < len(self.sorted_sportsmen):
                remaining_count = len(self.sorted_sportsmen) - self.current_team_index
                reply = QMessageBox.question(self, "Подтверждение", 
                                            f"Осталось неразмещенных команд: {remaining_count}. "
                                            "Вы уверены, что хотите завершить?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                    
            # Формируем результат
            result = {}
            for slot_num, team_data in self.placed_teams.items():
                result[slot_num] = [team_data[0], team_data[1], team_data[2]]
                
            self.result = result
            self.close()
            
    # Запуск приложения
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    window = ManualChoiceWindow()
    window.show()
    
    # Запускаем цикл событий
    app.exec_()
    
    # Возвращаем результат
    return window.result if hasattr(window, 'result') else {}

# # Пример использования
# if __name__ == "__main__":
#     # Пример данных
#     sorted_sportsmen = [
#         [1, "Команда А", "Москва", 100],
#         [2, "Команда Б", "СПб", 95],
#         [3, "Команда В", "Казань", 90],
#         [4, "Команда Г", "Нск", 85],
#         [5, "Команда Д", "Екб", 80],
#         [6, "Команда Е", "НН", 75],
#         [7, "Команда Ж", "Самара", 70],
#         [8, "Команда З", "Ростов", 65]
#     ]
    
#     count_exit = 2
#     free_num = []
#     posevs_num = [[1, 8], [4, 5], [2, 3, 6, 7]]
#     nums = [1]
def choice_manual(sorted_sportsmen, count_exit, free_num, posevs_num, nums):    
    result = choice_net_manual(sorted_sportsmen, count_exit, free_num, posevs_num, nums)
    return result
#     print("\nРезультат жеребьевки:")
#     if result:
#         for slot, team in sorted(result.items()):
#             print(f"Номер {slot}: {team[0]} ({team[1]}) - Рейтинг: {team[2]}")
#     else:
#         print("Жеребьевка не была завершена")