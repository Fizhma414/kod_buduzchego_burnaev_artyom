import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = self.load_data()

        # Поля ввода
        tk.Label(root, text="Сумма:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(root, text="Категория:").grid(row=1, column=0)
        self.category_cb = ttk.Combobox(root, values=["Еда", "Транспорт", "Развлечения", "Другое"])
        self.category_cb.grid(row=1, column=1)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0)
        self.date_entry = tk.Entry(root)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1)

        # Кнопки
        tk.Button(root, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(root, text="Показать всё / Сброс", command=self.update_table).grid(row=4, column=0, columnspan=2)

        # Фильтры
        tk.Label(root, text="Фильтр по категории:").grid(row=5, column=0)
        self.filter_cat = ttk.Combobox(root, values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Другое"])
        self.filter_cat.bind("<<ComboboxSelected>>", self.update_table)
        self.filter_cat.grid(row=5, column=1)

        # Таблица
        self.tree = ttk.Treeview(root, columns=("Сумма", "Категория", "Дата"), show='headings')
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Итог
        self.total_label = tk.Label(root, text="Итого: 0", font=('Arial', 12, 'bold'))
        self.total_label.grid(row=7, column=0, columnspan=2)

        self.update_table()

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_cb.get()
        date = self.date_entry.get()

        # Валидация
        try:
            if float(amount) <= 0: raise ValueError
        except ValueError:
            return messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return messagebox.showerror("Ошибка", "Формат даты: ГГГГ-ММ-ДД")

        if not category:
            return messagebox.showerror("Ошибка", "Выберите категорию")

        # Сохранение
        new_item = {"amount": float(amount), "category": category, "date": date}
        self.expenses.append(new_item)
        self.save_data()
        self.update_table()
        self.amount_entry.delete(0, tk.END)

    def update_table(self, event=None):
        # Очистка
        for i in self.tree.get_children():
            self.tree.delete(i)

        filter_cat = self.filter_cat.get()
        total = 0

        for exp in self.expenses:
            if filter_cat == "Все" or not filter_cat or exp['category'] == filter_cat:
                self.tree.insert("", "end", values=(exp['amount'], exp['category'], exp['date']))
                total += exp['amount']

        self.total_label.config(text=f"Итого: {total:.2f}")

    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
