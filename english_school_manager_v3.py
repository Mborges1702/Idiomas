import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class EnglishSchoolApp:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Gerenciador Escola de Inglês")
            self.root.geometry("1100x650")
            self.root.resizable(False, False)
            
            # Dados
            self.data_file = "escola_dados.json"
            self.data = self.load_data()
            self.current_student = None
            self.current_student_idx = None
            
            # Configuração de estilo
            style = ttk.Style()
            style.theme_use('clam')
            
            # Layout principal
            main_frame = ttk.Frame(root)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # PAINEL ESQUERDO
            left_frame = ttk.Frame(main_frame, width=200)
            left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
            left_frame.pack_propagate(False)
            
            ttk.Label(left_frame, text="ALUNOS", font=("Arial", 12, "bold")).pack(pady=10)
            
            btn_frame = ttk.Frame(left_frame)
            btn_frame.pack(fill="x", pady=5)
            ttk.Button(btn_frame, text="+ Novo", command=self.add_student).pack(fill="x", pady=2)
            ttk.Button(btn_frame, text="Remover", command=self.remove_student).pack(fill="x", pady=2)
            
            self.students_listbox = tk.Listbox(left_frame, width=25, height=25, font=("Arial", 10))
            self.students_listbox.pack(fill="both", expand=True, pady=10)
            self.students_listbox.bind("<<ListboxSelect>>", self.on_student_select)
            
            # PAINEL DIREITO
            self.right_frame = ttk.Frame(main_frame)
            self.right_frame.pack(side="right", fill="both", expand=True)
            
            self.detail_notebook = ttk.Notebook(self.right_frame)
            self.detail_notebook.pack(fill="both", expand=True)
            
            # Criar abas
            self.info_tab = ttk.Frame(self.detail_notebook)
            self.detail_notebook.add(self.info_tab, text="Informações")
            
            self.payments_tab = ttk.Frame(self.detail_notebook)
            self.detail_notebook.add(self.payments_tab, text="Mensalidades")
            
            self.classes_tab = ttk.Frame(self.detail_notebook)
            self.detail_notebook.add(self.classes_tab, text="Aulas")
            
            self.activities_tab = ttk.Frame(self.detail_notebook)
            self.detail_notebook.add(self.activities_tab, text="Atividades")
            
            # Botão SALVAR
            save_btn = ttk.Button(root, text="💾 SALVAR TUDO", command=self.save_data_button, width=30)
            save_btn.pack(pady=10)
            
            self.refresh_students_list()
            
        except Exception as e:
            messagebox.showerror("Erro na inicialização", f"Erro: {str(e)}")
            raise
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_data()
        return self.default_data()
    
    def default_data(self):
        return {
            "students": [],
            "payments": [],
            "classes": [],
            "activities": []
        }
    
    def save_data_button(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("✓ Salvo", "Todos os dados foram salvos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    # ===== LISTA DE ALUNOS =====
    def refresh_students_list(self):
        self.students_listbox.delete(0, "end")
        for idx, student in enumerate(self.data["students"]):
            self.students_listbox.insert("end", student["name"])
    
    def on_student_select(self, event):
        selection = self.students_listbox.curselection()
        if not selection:
            return
        
        self.current_student_idx = selection[0]
        self.current_student = self.data["students"][self.current_student_idx]
        self.refresh_detail_tabs()
    
    def add_student(self):
        window = tk.Toplevel(self.root)
        window.title("Novo Aluno")
        window.geometry("300x200")
        window.resizable(False, False)
        
        ttk.Label(window, text="Nome:").pack(padx=10, pady=5)
        name_entry = ttk.Entry(window, width=30)
        name_entry.pack(padx=10, pady=5)
        name_entry.focus()
        
        ttk.Label(window, text="Email (opcional):").pack(padx=10, pady=5)
        email_entry = ttk.Entry(window, width=30)
        email_entry.pack(padx=10, pady=5)
        
        ttk.Label(window, text="Telefone (opcional):").pack(padx=10, pady=5)
        phone_entry = ttk.Entry(window, width=30)
        phone_entry.pack(padx=10, pady=5)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Aviso", "Nome obrigatório!")
                return
            
            student = {
                "id": str(len(self.data["students"]) + 1),
                "name": name,
                "email": email_entry.get().strip(),
                "phone": phone_entry.get().strip()
            }
            
            self.data["students"].append(student)
            self.refresh_students_list()
            window.destroy()
            messagebox.showinfo("✓", f"Aluno '{name}' adicionado!")
        
        ttk.Button(window, text="Salvar", command=save).pack(pady=20)
    
    def remove_student(self):
        if not self.current_student:
            messagebox.showwarning("Aviso", "Selecione um aluno!")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover '{self.current_student['name']}'?"):
            student_id = self.current_student["id"]
            self.data["students"].pop(self.current_student_idx)
            
            self.data["payments"] = [p for p in self.data["payments"] if p["student_id"] != student_id]
            self.data["activities"] = [a for a in self.data["activities"] if a["student_id"] != student_id]
            
            self.current_student = None
            self.current_student_idx = None
            self.refresh_students_list()
            self.refresh_detail_tabs()
            messagebox.showinfo("✓", "Aluno removido!")
    
    # ===== ABA INFORMAÇÕES =====
    def refresh_info_tab(self):
        for widget in self.info_tab.winfo_children():
            widget.destroy()
        
        if not self.current_student:
            ttk.Label(self.info_tab, text="Selecione um aluno", foreground="gray").pack(pady=20)
            return
        
        student = self.current_student
        
        frame = ttk.Frame(self.info_tab)
        frame.pack(padx=20, pady=20, anchor="nw", fill="x")
        
        ttk.Label(frame, text=student["name"], font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        ttk.Label(frame, text=f"Email: {student.get('email', 'Não informado')}").pack(anchor="w", pady=5)
        ttk.Label(frame, text=f"Telefone: {student.get('phone', 'Não informado')}").pack(anchor="w", pady=5)
    
    # ===== ABA MENSALIDADES =====
    def refresh_payments_tab(self):
        for widget in self.payments_tab.winfo_children():
            widget.destroy()
        
        if not self.current_student:
            ttk.Label(self.payments_tab, text="Selecione um aluno", foreground="gray").pack(pady=20)
            return
        
        student = self.current_student
        
        ttk.Label(self.payments_tab, text=f"Mensalidades de {student['name']}", font=("Arial", 11, "bold")).pack(padx=10, pady=10)
        
        # Frame com canvas para scroll
        canvas_frame = ttk.Frame(self.payments_tab)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid de meses
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        current_year = datetime.now().year
        
        for row, month in enumerate(months):
            month_label = ttk.Label(scrollable_frame, text=f"{month}/{current_year}", font=("Arial", 9, "bold"), width=12)
            month_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            payment = next(
                (p for p in self.data["payments"] 
                 if p["student_id"] == student["id"] and p["month"] == row + 1 and p["year"] == current_year),
                None
            )
            
            is_paid = payment and payment.get("paid", False)
            btn_text = "✓ PAGO" if is_paid else "Pendente"
            
            def make_toggle(month_num=row + 1, year=current_year):
                def toggle_payment():
                    payment = next(
                        (p for p in self.data["payments"] 
                         if p["student_id"] == student["id"] and p["month"] == month_num and p["year"] == year),
                        None
                    )
                    
                    if payment:
                        payment["paid"] = not payment.get("paid", False)
                    else:
                        self.data["payments"].append({
                            "student_id": student["id"],
                            "month": month_num,
                            "year": year,
                            "paid": True,
                            "paid_date": datetime.now().strftime("%d/%m/%Y")
                        })
                    
                    self.refresh_payments_tab()
                
                return toggle_payment
            
            btn = ttk.Button(scrollable_frame, text=btn_text, command=make_toggle(), width=15)
            btn.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    # ===== ABA AULAS =====
    def refresh_classes_tab(self):
        for widget in self.classes_tab.winfo_children():
            widget.destroy()
        
        if not self.current_student:
            ttk.Label(self.classes_tab, text="Selecione um aluno", foreground="gray").pack(pady=20)
            return
        
        student = self.current_student
        
        ttk.Label(self.classes_tab, text=f"Aulas de {student['name']}", font=("Arial", 11, "bold")).pack(padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.classes_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="+ Nova Aula", command=lambda: self.add_class_window(student["id"])).pack(side="left", padx=5)
        
        classes = [c for c in self.data["classes"] if student["id"] in c.get("students", [])]
        
        if not classes:
            ttk.Label(self.classes_tab, text="Sem aulas registradas", foreground="gray").pack(pady=20)
            return
        
        for cls in classes:
            class_label = ttk.Label(
                self.classes_tab,
                text=f"📅 {cls['date']} às {cls['time']} - {cls['topic']}",
                font=("Arial", 9)
            )
            class_label.pack(anchor="w", padx=20, pady=3)
    
    def add_class_window(self, student_id):
        window = tk.Toplevel(self.root)
        window.title("Nova Aula")
        window.geometry("300x200")
        window.resizable(False, False)
        
        ttk.Label(window, text="Data (DD/MM/YYYY):").pack(padx=10, pady=5)
        date_entry = ttk.Entry(window, width=25)
        date_entry.pack(padx=10, pady=5)
        
        ttk.Label(window, text="Hora (HH:MM):").pack(padx=10, pady=5)
        time_entry = ttk.Entry(window, width=25)
        time_entry.pack(padx=10, pady=5)
        
        ttk.Label(window, text="Tema:").pack(padx=10, pady=5)
        topic_entry = ttk.Entry(window, width=25)
        topic_entry.pack(padx=10, pady=5)
        
        def save():
            if not date_entry.get() or not time_entry.get() or not topic_entry.get():
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            cls = {
                "id": str(len(self.data["classes"]) + 1),
                "date": date_entry.get(),
                "time": time_entry.get(),
                "topic": topic_entry.get(),
                "students": [student_id]
            }
            
            self.data["classes"].append(cls)
            self.refresh_detail_tabs()
            window.destroy()
            messagebox.showinfo("✓", "Aula adicionada!")
        
        ttk.Button(window, text="Salvar", command=save).pack(pady=20)
    
    # ===== ABA ATIVIDADES =====
    def refresh_activities_tab(self):
        for widget in self.activities_tab.winfo_children():
            widget.destroy()
        
        if not self.current_student:
            ttk.Label(self.activities_tab, text="Selecione um aluno", foreground="gray").pack(pady=20)
            return
        
        student = self.current_student
        
        ttk.Label(self.activities_tab, text=f"Atividades de {student['name']}", font=("Arial", 11, "bold")).pack(padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.activities_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="+ Nova Atividade", command=lambda: self.add_activity_window(student["id"])).pack(side="left", padx=5)
        
        activities = [a for a in self.data["activities"] if a["student_id"] == student["id"]]
        
        if not activities:
            ttk.Label(self.activities_tab, text="Sem atividades registradas", foreground="gray").pack(pady=20)
            return
        
        for activity in activities:
            status_emoji = "✓" if activity.get("status") == "Entregue" else "⏳"
            grade_text = f" | Nota: {activity.get('grade', '-')}" if activity.get('grade') != '-' else ""
            
            activity_label = ttk.Label(
                self.activities_tab,
                text=f"{status_emoji} {activity['title']} | Prazo: {activity['due_date']}{grade_text}",
                font=("Arial", 9)
            )
            activity_label.pack(anchor="w", padx=20, pady=3)
    
    def add_activity_window(self, student_id):
        window = tk.Toplevel(self.root)
        window.title("Nova Atividade")
        window.geometry("300x250")
        window.resizable(False, False)
        
        ttk.Label(window, text="Título:").pack(padx=10, pady=5)
        title_entry = ttk.Entry(window, width=25)
        title_entry.pack(padx=10, pady=5)
        
        ttk.Label(window, text="Prazo (DD/MM/YYYY):").pack(padx=10, pady=5)
        due_entry = ttk.Entry(window, width=25)
        due_entry.pack(padx=10, pady=5)
        
        ttk.Label(window, text="Status:").pack(padx=10, pady=5)
        status_combo = ttk.Combobox(window, values=["Pendente", "Entregue"], width=22, state="readonly")
        status_combo.set("Pendente")
        status_combo.pack(padx=10, pady=5)
        
        def save():
            if not title_entry.get() or not due_entry.get():
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            activity = {
                "id": str(len(self.data["activities"]) + 1),
                "student_id": student_id,
                "title": title_entry.get(),
                "due_date": due_entry.get(),
                "status": status_combo.get(),
                "grade": "-"
            }
            
            self.data["activities"].append(activity)
            self.refresh_detail_tabs()
            window.destroy()
            messagebox.showinfo("✓", "Atividade adicionada!")
        
        ttk.Button(window, text="Salvar", command=save).pack(pady=20)
    
    def refresh_detail_tabs(self):
        try:
            self.refresh_info_tab()
        except Exception as e:
            print(f"Erro refresh_info_tab: {e}")
        
        try:
            self.refresh_payments_tab()
        except Exception as e:
            print(f"Erro refresh_payments_tab: {e}")
        
        try:
            self.refresh_classes_tab()
        except Exception as e:
            print(f"Erro refresh_classes_tab: {e}")
        
        try:
            self.refresh_activities_tab()
        except Exception as e:
            print(f"Erro refresh_activities_tab: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = EnglishSchoolApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
