import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from dotenv import load_dotenv
from app import fetch_all_ads, save_results
from constants import DEFAULT_COUNTRY, DEFAULT_LIMIT, API_FIELDS
import time

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

class AdSpyGUI:
    def __init__(self, root):
        self.root = root
        root.title("ADSpy - Facebook Ad Library")
        root.geometry("700x520")
        
        frm = ttk.Frame(root, padding=10)
        frm.pack(fill="both", expand=True)
        
        row = 0
        ttk.Label(frm, text="Country (ISO):").grid(column=0, row=row, sticky="w")
        self.country_var = tk.StringVar(value=DEFAULT_COUNTRY)
        ttk.Entry(frm, textvariable=self.country_var, width=10).grid(column=1, row=row, sticky="w")
        
        ttk.Label(frm, text="Keyword:").grid(column=2, row=row, sticky="w", padx=(10,0))
        self.keyword_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.keyword_var, width=30).grid(column=3, row=row, sticky="w")
        
        row += 1
        ttk.Label(frm, text="Limit (per page):").grid(column=0, row=row, sticky="w", pady=(8,0))
        self.limit_var = tk.IntVar(value=DEFAULT_LIMIT)
        ttk.Spinbox(frm, from_=1, to=100, textvariable=self.limit_var, width=6).grid(column=1, row=row, sticky="w", pady=(8,0))
        
        self.start_btn = ttk.Button(frm, text="Start Fetch", command=self.start_fetch)
        self.start_btn.grid(column=3, row=row, sticky="e", padx=(0,10), pady=(8,0))
        
        row += 1
        ttk.Separator(frm, orient="horizontal").grid(column=0, row=row, columnspan=4, sticky="ew", pady=8)
        
        row += 1
        ttk.Label(frm, text="Status / Results:").grid(column=0, row=row, sticky="w")
        row += 1
        self.output = scrolledtext.ScrolledText(frm, wrap="word", height=20)
        self.output.grid(column=0, row=row, columnspan=4, sticky="nsew")
        frm.rowconfigure(row, weight=1)
        
        # Disable start if no token
        if not ACCESS_TOKEN:
            messagebox.showerror("Missing ACCESS_TOKEN", "ACCESS_TOKEN not found in .env. Please add it and restart.")
            self.start_btn.config(state="disabled")
    
    def append(self, text):
        self.output.insert("end", text + "\n")
        self.output.see("end")
    
    def start_fetch(self):
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showwarning("Missing keyword", "Please enter a search keyword.")
            return
        self.start_btn.config(state="disabled")
        self.append(f"🔎 Starting fetch for '{keyword}' in {self.country_var.get()} ...")
        thread = threading.Thread(target=self.worker, daemon=True)
        thread.start()
    
    def worker(self):
        country = self.country_var.get().strip() or DEFAULT_COUNTRY
        keyword = self.keyword_var.get().strip()
        limit = int(self.limit_var.get() or DEFAULT_LIMIT)
        
        params = {
            "access_token": ACCESS_TOKEN,
            "ad_reached_countries": country,
            "ad_active_status": "ALL",
            "ad_type": "ALL",
            "search_terms": keyword,
            "limit": limit,
            "fields": API_FIELDS,
        }
        
        start = time.time()
        try:
            ads = fetch_all_ads(params)
        except Exception as e:
            self.root.after(0, lambda: self.append(f"❌ Error during fetch: {e}"))
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            return
        
        duration = time.time() - start
        # schedule UI update on main thread
        self.root.after(0, lambda: self.on_fetch_done(ads, country, keyword, duration))
    
    def on_fetch_done(self, ads, country, keyword, duration):
        if not ads:
            self.append("⚠️ No ads found or an error occurred.")
        else:
            self.append(f"✅ Fetch completed: found {len(ads)} ads (took {duration:.1f}s).")
            # show first few ads summary
            for i, ad in enumerate(ads[:10], start=1):
                title = ", ".join(ad.get("ad_creative_link_titles", [])) or "—"
                page = ad.get("page_name", "Unknown")
                self.append(f"[{i}] {page} — {title}")
        # Auto-save
        try:
            save_results(ads, country=country, search_term=keyword)
            self.append("✅ Results saved.")
        except Exception as e:
            self.append(f"⚠️ Failed to save results: {e}")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdSpyGUI(root)
    root.mainloop()