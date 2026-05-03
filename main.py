import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime

# --- ЛОГИКА РАБОТЫ С ДАННЫМИ ---
class DataManager:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = self.load_data()

    def load_data(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def add_item(self, amount, category, date):
        self.expenses.append({"amount": float(amount), "category": category, "date": date})
        self.save_data()

    def get_filtered_data(self, category_filter="Все", start_date=None, end_date=None):
        filtered = []
        for exp in self.expenses:
            # Фильтр по категории
            cat_match = (category_filter == "Все" or exp['category'] == category_filter)
            
            # Фильтр по дате
            date_obj = datetime.strptime(exp['date'], "%Y-%m-%d")
            date_match = True
            if start_date:
                date_match &= (date_obj >= start_date)
            if end_date:
                date_match &= (date_obj <= end_date)
            
            if cat_match and date_match:
                filtered.append(exp)
        return filtered

# --- ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ---
class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker Pro")
        self.data_manager = DataManager()

        # Блок ввода данных
        input_frame = tk.LabelFrame(root, text="Добавить новый расход", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Категория:").grid(row=1, column=0)
        self.category_cb = ttk.Combobox(input_frame, values=["Еда", "Транспорт", "Развлечения", "Другое"])
        self.category_cb.grid(row=1, column=1)

        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0)
        self.date_entry = tk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1)

        tk.Button(input_frame, text="Добавить расход", command=self.add_expense, bg="#e1ebe1").grid(row=3, column=0, columnspan=2, pady=10)

        # Блок фильтрации
        filter_frame = tk.LabelFrame(root, text="Фильтры и поиск", padx=10, pady=10)
        filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0)
        self.filter_cat = ttk.Combobox(filter_frame, values=["Все", "Еда", "Транспорт", "Развлечения", "Другое"])
        self.filter_cat.set("Все")
        self.filter_cat.grid(row=0, column=1)

        tk.Label(filter_frame, text="От (ГГГГ-ММ-ДД):").grid(row=1, column=0)
        self.start_date_entry = tk.Entry(filter_frame)
        self.start_date_entry.grid(row=1, column=1)

        tk.Label(filter_frame, text="До (ГГГГ-ММ-ДД):").grid(row=2, column=0)
        self.end_date_entry = tk.Entry(filter_frame)
        self.end_date_entry.grid(row=2, column=1)

        tk.Button(filter_frame, text="Применить фильтр", command=self.update_table).grid(row=3, column=0, columnspan=2, pady=5)

        # Таблица
        self.tree = ttk.Treeview(root, columns=("Сумма", "Категория", "Дата"), show='headings')
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Итог
        self.total_label = tk.Label(root, text="Итого: 0.00", font=('Arial', 14, 'bold'), fg="blue")
        self.total_label.grid(row=2, column=0, columnspan=2, pady=5)

        self.update_table()

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_cb.get()
        date = self.date_entry.get()

        try:
            if float(amount) <= 0: raise ValueError
            datetime.strptime(date, "%Y-%m-%d")
            if not category: raise IndexError
        except ValueError:
            return messagebox.showerror("Ошибка", "Проверьте сумму (число > 0) и формат даты (ГГГГ-ММ-ДД)")
        except IndexError:
            return messagebox.showerror("Ошибка", "Выберите категорию")

        self.data_manager.add_item(amount, category, date)
        self.update_table()
        self.amount_entry.delete(0, tk.END)

    def update_table(self):
        # Очистка таблицы
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Получение дат для фильтра
        s_date = None
        e_date = None
        try:
            if self.start_date_entry.get():
                s_date = datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d")
            if self.end_date_entry.get():
                e_date = datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Внимание", "Неверный формат даты в фильтре (используйте ГГГГ-ММ-ДД)")

        # Запрос отфильтрованных данных
        items = self.data_manager.get_filtered_data(self.filter_cat.get(), s_date, e_date)
        
        total = 0
        for exp in items:
            self.tree.insert("", "end", values=(f"{exp['amount']:.2f}", exp['category'], exp['date']))
            total += exp['amount']

        self.total_label.config(text=f"Итого за период: {total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()
