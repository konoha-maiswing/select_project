import sys
import datetime
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QLineEdit, QDateEdit, QComboBox, QPushButton,
    QCheckBox, QTabWidget, QTableWidgetItem, QLabel
)
from PySide6.QtCore import Qt, QDate, QTimer

DATA_FILE = Path("tasks.json")


# =======================
# タスクデータ
# =======================
class Task: #タスクの情報まとめ
    def __init__(self, content, date, importance, exp,
                 done=False, completed_date=None, active=False):
        self.content = content # タスクの内容
        self.date = date # 日付
        self.importance = importance # 重要度
        self.exp = exp #獲得経験値
        self.done = done # 完了したか
        self.completed_date = completed_date # 完了日
        self.active = active # アクティブか

    def to_dict(self): # Json
        return {
            "content": self.content,
            "date": self.date.isoformat(),
            "importance": self.importance,
            "exp": self.exp,
            "done": self.done,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "active": self.active
        }

    @staticmethod 
    def from_dict(data):
        return Task(
            data["content"],
            datetime.date.fromisoformat(data["date"]),
            data["importance"],
            data.get("exp", 5),
            data["done"],
            datetime.date.fromisoformat(data["completed_date"])
            if data.get("completed_date") else None,
            data.get("active", False)
        )


# =======================
# ルーティンデータ
# =======================
class Routine:
    def __init__(self, content, exp, done=False, last_done=None): # ルーティンの内容
        self.content = content
        self.exp = exp
        self.done = done
        self.last_done = last_done # 最後に完了した日

    def to_dict(self):
        return {
            "content": self.content,
            "exp": self.exp,
            "done": self.done,
            "last_done": self.last_done.isoformat() if self.last_done else None
        }

    @staticmethod
    def from_dict(data):
        return Routine(
            data["content"],
            data["exp"],
            data.get("done", False),
            datetime.date.fromisoformat(data["last_done"])
            if data.get("last_done") else None
        )


# =======================
# メインアプリ
# =======================
class TaskApp(QWidget):
    def __init__(self):
        super().__init__()

        # ===== 状態 =====
        self.tasks = []
        self.routines = []
        self.prev_level = 1

        self.setWindowTitle("タスク管理アプリ")

        # ===== レイアウト（8:4）=====
        self.layout = QHBoxLayout(self)
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.left_layout, 8)
        self.layout.addLayout(self.right_layout, 4)

        # ===== 日付 =====
        self.date_label = QLabel(alignment=Qt.AlignCenter)
        self.date_label.setStyleSheet("font-size:16px;font-weight:bold;")
        self.left_layout.addWidget(self.date_label)

        # ===== レベル =====
        level_layout = QHBoxLayout()
        self.levelup_label = QLabel("レベルアップ！")
        self.levelup_label.setStyleSheet("color:red;font-weight:bold;")
        self.levelup_label.hide()

        self.level_label = QLabel()
        self.level_label.setStyleSheet("color:#8e44ad;")

        level_layout.addStretch()
        level_layout.addWidget(self.levelup_label)
        level_layout.addSpacing(10)
        level_layout.addWidget(self.level_label)
        level_layout.addStretch()
        self.left_layout.addLayout(level_layout)

        # ===== タスク入力 =====
        form = QHBoxLayout() # 横方向の配置
        self.task_input = QLineEdit(placeholderText="タスク内容")
        self.date_input = QDateEdit(QDate.currentDate(), calendarPopup=True)

        self.importance_input = QComboBox()
        self.importance_input.addItems(["★", "★★", "★★★", "★★★★", "★★★★★"])

        self.exp_input = QLineEdit(placeholderText="EXP")

        add_btn = QPushButton("追加")
        add_btn.clicked.connect(self.add_task)

        for w in [self.task_input, self.date_input,
                  self.importance_input, self.exp_input, add_btn]:
            form.addWidget(w)

        self.left_layout.addLayout(form)

        # ===== タブ =====
        self.tabs = QTabWidget()
        self.left_layout.addWidget(self.tabs)

        self.today_table = self.create_table()
        self.tabs.addTab(self.today_table, "📅 今日")

        self.all_table = self.create_table()
        self.tabs.addTab(self.all_table, "📋 全部")

        self.archive_table = self.create_table()
        self.tabs.addTab(self.archive_table, "🗃 完了")

        self.active_table = self.create_table()
        self.tabs.addTab(self.active_table, "⚡ アクティブ")

        # ===== ルーティン入力 =====
        routine_form = QHBoxLayout()
        self.routine_input = QLineEdit(placeholderText="ルーティン内容")
        self.routine_exp = QLineEdit(placeholderText="EXP")
        add_routine_btn = QPushButton("追加")
        add_routine_btn.clicked.connect(self.add_routine)

        for w in [self.routine_input, self.routine_exp, add_routine_btn]:
            routine_form.addWidget(w)

        self.right_layout.addLayout(routine_form)

        # ===== ルーティン表 =====
        title = QLabel("🔁 毎日のルーティン")
        title.setStyleSheet("font-weight:bold;")
        self.right_layout.addWidget(title)

        self.routine_table = QTableWidget()
        self.routine_table.setColumnCount(4)
        self.routine_table.setHorizontalHeaderLabels(
            ["完了", "内容", "EXP", "削除"]
        )
        self.routine_table.setColumnWidth(0, 50)
        self.routine_table.setColumnWidth(1, 180)
        self.routine_table.setColumnWidth(2, 60)
        self.routine_table.setColumnWidth(3, 60)
        self.routine_table.verticalHeader().setVisible(False)
        self.right_layout.addWidget(self.routine_table)

        # ===== タイマー =====
        timer = QTimer(self)
        timer.timeout.connect(self.update_header)
        timer.start(60000)

        self.load_tasks()
        self.refresh()

    # =======================
    # レベル
    # =======================
    def calculate_level(self, total_exp):
        return total_exp // 50 + 1, total_exp % 50, 50

    def update_header(self):
        today = datetime.date.today()
        week = "月火水木金土日"
        self.date_label.setText(
            f"📅 今日：{today.strftime('%Y年%m月%d日')}（{week[today.weekday()]}）"
        )

        total_exp = (
            sum(t.exp for t in self.tasks if t.done) +
            sum(r.exp for r in self.routines
                if r.done and r.last_done == today)
        )

        level, current, need = self.calculate_level(total_exp)
        if level > self.prev_level:
            self.levelup_label.show()
            QTimer.singleShot(3000, self.levelup_label.hide)

        self.prev_level = level
        self.level_label.setText(f"🏆 Lv.{level}｜EXP {current}/{need}")

    # =======================
    # タスク
    # =======================
    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            ["完了", "アクティブ", "内容", "重要度", "EXP", "日付", "削除"]
        )
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 70)
        table.setColumnWidth(3, 70)
        table.setColumnWidth(4, 50)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 60)
        table.verticalHeader().setVisible(False)
        return table

    def add_task(self): # タスクの追加
        if not self.task_input.text().strip():
            return
        try:
            exp = int(self.exp_input.text())
        except ValueError:
            exp = 5

        self.tasks.append(Task(
            self.task_input.text(),
            self.date_input.date().toPython(),
            self.importance_input.currentText(),
            exp
        ))
        self.task_input.clear()
        self.exp_input.clear()
        self.save_tasks()
        self.refresh()

    def delete_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.save_tasks()
            self.refresh()

    def refresh(self):
        for t in [self.today_table, self.all_table,
                  self.archive_table, self.active_table]:
            t.setRowCount(0)

        today = datetime.date.today()
        active = [t for t in self.tasks if not t.done]
        done = [t for t in self.tasks if t.done]

        for t in [x for x in active if x.date <= today or x.active]:
            self.add_row(t, self.today_table)
        for t in active:
            self.add_row(t, self.all_table)
        for t in done:
            self.add_row(t, self.archive_table)
        for t in active:
            if t.active:
                self.add_row(t, self.active_table)

        self.refresh_routines()
        self.update_header()

    def add_row(self, task, table):
        r = table.rowCount()
        table.insertRow(r)

        cb_done = QCheckBox()
        cb_done.setChecked(task.done)
        cb_done.stateChanged.connect(lambda _, t=task: self.toggle_done(t))
        table.setCellWidget(r, 0, cb_done)

        cb_active = QCheckBox()
        cb_active.setChecked(task.active)
        cb_active.stateChanged.connect(lambda _, t=task: self.toggle_active(t))
        table.setCellWidget(r, 1, cb_active)

        table.setItem(r, 2, QTableWidgetItem(task.content))
        table.setItem(r, 3, QTableWidgetItem(task.importance))
        table.setItem(r, 4, QTableWidgetItem(str(task.exp)))

        week = "月火水木金土日"
        date_text = f"{task.date.month:02}/{task.date.day:02}（{week[task.date.weekday()]}）"
        table.setItem(r, 5, QTableWidgetItem(date_text))

        del_btn = QPushButton("削除")
        del_btn.clicked.connect(lambda _, t=task: self.delete_task(t))
        table.setCellWidget(r, 6, del_btn)

    def toggle_done(self, task):
        task.done = not task.done
        task.completed_date = datetime.date.today() if task.done else None
        self.save_tasks()
        self.refresh()

    def toggle_active(self, task):
        task.active = not task.active
        self.save_tasks()
        self.refresh()

    # =======================
    # ルーティン
    # =======================
    def add_routine(self):
        if not self.routine_input.text().strip():
            return
        try:
            exp = int(self.routine_exp.text())
        except ValueError:
            exp = 5

        self.routines.append(Routine(self.routine_input.text(), exp))
        self.routine_input.clear()
        self.routine_exp.clear()
        self.save_tasks()
        self.refresh()

    def delete_routine(self, routine):
        if routine in self.routines:
            self.routines.remove(routine)
            self.save_tasks()
            self.refresh()

    def refresh_routines(self):
        self.routine_table.setRowCount(0)
        today = datetime.date.today()

        for r in self.routines:
            if r.last_done != today:
                r.done = False

            row = self.routine_table.rowCount()
            self.routine_table.insertRow(row)

            cb = QCheckBox()
            cb.setChecked(r.done)
            cb.stateChanged.connect(lambda _, rt=r: self.toggle_routine(rt))
            self.routine_table.setCellWidget(row, 0, cb)

            self.routine_table.setItem(row, 1, QTableWidgetItem(r.content))
            self.routine_table.setItem(row, 2, QTableWidgetItem(str(r.exp)))

            del_btn = QPushButton("削除")
            del_btn.clicked.connect(lambda _, rt=r: self.delete_routine(rt))
            self.routine_table.setCellWidget(row, 3, del_btn)

    def toggle_routine(self, routine):
        routine.done = not routine.done
        if routine.done:
            routine.last_done = datetime.date.today()
        self.save_tasks()
        self.refresh()

    # =======================
    # 保存 / 読込
    # =======================
    def save_tasks(self):
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "routines": [r.to_dict() for r in self.routines]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.tasks = [Task.from_dict(d) for d in data]
                self.routines = []
            else:
                self.tasks = [Task.from_dict(d) for d in data.get("tasks", [])]
                self.routines = [
                    Routine.from_dict(d) for d in data.get("routines", [])
                ]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TaskApp()
    w.resize(1200, 680)
    w.show()
    sys.exit(app.exec())
