from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def sanitize_text(text: str) -> str:
	return "".join(character for character in text.upper() if character.isalpha()).replace("J", "I")


def filler_for(character: str) -> str:
	return "Q" if character == "X" else "X"


def build_key_square(key: str) -> tuple[list[list[str]], dict[str, tuple[int, int]]]:
	cleaned_key = sanitize_text(key)
	seen: set[str] = set()
	sequence: list[str] = []

	for character in cleaned_key + ALPHABET:
		if character in ALPHABET and character not in seen:
			seen.add(character)
			sequence.append(character)

	square = [sequence[index : index + 5] for index in range(0, 25, 5)]
	positions = {
		character: (row_index, column_index)
		for row_index, row in enumerate(square)
		for column_index, character in enumerate(row)
	}
	return square, positions


def prepare_pairs(text: str) -> list[tuple[str, str]]:
	cleaned = sanitize_text(text)
	pairs: list[tuple[str, str]] = []
	index = 0

	while index < len(cleaned):
		first = cleaned[index]

		if index + 1 >= len(cleaned):
			pairs.append((first, filler_for(first)))
			index += 1
			continue

		second = cleaned[index + 1]
		if first == second:
			pairs.append((first, filler_for(first)))
			index += 1
		else:
			pairs.append((first, second))
			index += 2

	return pairs


def format_pairs(pairs: list[tuple[str, str]]) -> str:
	return " ".join(f"{first}{second}" for first, second in pairs)


def chunk_text(text: str) -> list[tuple[str, str]]:
	cleaned = sanitize_text(text)
	if len(cleaned) % 2 == 1:
		cleaned += "X"
	return [(cleaned[index], cleaned[index + 1]) for index in range(0, len(cleaned), 2)]


def encrypt_pair(first: str, second: str, positions: dict[str, tuple[int, int]], square: list[list[str]]) -> tuple[str, str]:
	row1, col1 = positions[first]
	row2, col2 = positions[second]

	if row1 == row2:
		return square[row1][(col1 + 1) % 5], square[row2][(col2 + 1) % 5]
	if col1 == col2:
		return square[(row1 + 1) % 5][col1], square[(row2 + 1) % 5][col2]
	return square[row1][col2], square[row2][col1]


def decrypt_pair(first: str, second: str, positions: dict[str, tuple[int, int]], square: list[list[str]]) -> tuple[str, str]:
	row1, col1 = positions[first]
	row2, col2 = positions[second]

	if row1 == row2:
		return square[row1][(col1 - 1) % 5], square[row2][(col2 - 1) % 5]
	if col1 == col2:
		return square[(row1 - 1) % 5][col1], square[(row2 - 1) % 5][col2]
	return square[row1][col2], square[row2][col1]


def encrypt_text(text: str, key: str) -> str:
	square, positions = build_key_square(key)
	pairs = prepare_pairs(text)
	encrypted = ["".join(encrypt_pair(first, second, positions, square)) for first, second in pairs]
	return "".join(encrypted)


def decrypt_text(text: str, key: str) -> str:
	square, positions = build_key_square(key)
	pairs = chunk_text(text)
	decrypted = ["".join(decrypt_pair(first, second, positions, square)) for first, second in pairs]
	return "".join(decrypted)


def remove_inserted_fillers(text: str) -> str:
	cleaned = sanitize_text(text)
	if not cleaned:
		return ""

	result: list[str] = []
	index = 0

	while index < len(cleaned):
		if (
			index + 2 < len(cleaned)
			and cleaned[index] == cleaned[index + 2]
			and cleaned[index + 1] == filler_for(cleaned[index])
		):
			result.append(cleaned[index])
			index += 2
			continue

		result.append(cleaned[index])
		index += 1

	if len(result) >= 2 and result[-1] == filler_for(result[-2]):
		result.pop()

	return "".join(result)


class PlayfairApp(tk.Tk):
	def __init__(self) -> None:
		super().__init__()
		self.title("Playfair Cipher Tool")
		self.geometry("900x640")
		self.minsize(820, 560)

		self.key_var = tk.StringVar(value="MONARCHY")
		self.status_var = tk.StringVar(value="Enter a key and text, then choose Encrypt or Decrypt.")

		self._build_styles()
		self._build_layout()
		self._refresh_square()

	def _build_styles(self) -> None:
		style = ttk.Style(self)
		try:
			style.theme_use("clam")
		except tk.TclError:
			pass

		style.configure("App.TFrame", padding=12)
		style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
		style.configure("Info.TLabel", font=("Segoe UI", 9))
		style.configure("Matrix.TLabel", font=("Consolas", 16, "bold"), anchor="center")
		style.configure("ActionBlue.TButton", padding=(14, 8), background="#1D4ED8", foreground="white", borderwidth=1)
		style.map("ActionBlue.TButton", background=[("active", "#1E40AF"), ("pressed", "#1E3A8A")])

		style.configure("ActionYellow.TButton", padding=(14, 8), background="#FACC15", foreground="#1F2937", borderwidth=1)
		style.map("ActionYellow.TButton", background=[("active", "#EAB308"), ("pressed", "#CA8A04")])

		style.configure("ActionGreen.TButton", padding=(14, 8), background="#16A34A", foreground="white", borderwidth=1)
		style.map("ActionGreen.TButton", background=[("active", "#15803D"), ("pressed", "#166534")])

	def _build_layout(self) -> None:
		container = ttk.Frame(self, style="App.TFrame")
		container.pack(fill="both", expand=True)

		header = ttk.Frame(container)
		header.pack(fill="x", pady=(0, 10))

		ttk.Label(header, text="Playfair Cipher", style="Header.TLabel").pack(anchor="w")
		ttk.Label(
			header,
			text="I and J share one cell. Letters only are used for the cipher; spacing and punctuation are ignored.",
			style="Info.TLabel",
		).pack(anchor="w", pady=(4, 0))

		top = ttk.Frame(container)
		top.pack(fill="x", pady=(0, 12))

		key_frame = ttk.LabelFrame(top, text="Key")
		key_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

		self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var)
		self.key_entry.pack(fill="x", padx=10, pady=10)
		self.key_entry.bind("<KeyRelease>", lambda _event: self._refresh_square())

		matrix_frame = ttk.LabelFrame(top, text="Key Square")
		matrix_frame.pack(side="right", fill="both", expand=False)

		self.matrix_labels: list[ttk.Label] = []
		grid = ttk.Frame(matrix_frame)
		grid.pack(padx=10, pady=10)

		for row in range(5):
			for column in range(5):
				label = ttk.Label(grid, text=" ", width=3, style="Matrix.TLabel", relief="ridge")
				label.grid(row=row, column=column, padx=2, pady=2, ipadx=6, ipady=6, sticky="nsew")
				self.matrix_labels.append(label)

		for row in range(5):
			grid.grid_rowconfigure(row, weight=1)
		for column in range(5):
			grid.grid_columnconfigure(column, weight=1)

		editor = ttk.Frame(container)
		editor.pack(fill="both", expand=True)

		left = ttk.LabelFrame(editor, text="Plaintext")
		left.pack(side="left", fill="both", expand=True, padx=(0, 10))

		self.plain_text = tk.Text(left, wrap="word", height=12, undo=True)
		self.plain_text.pack(fill="both", expand=True, padx=10, pady=(10, 6))

		left_button_row = ttk.Frame(left)
		left_button_row.pack(fill="x", padx=10, pady=(0, 10))

		ttk.Button(left_button_row, text="Encrypt", style="ActionBlue.TButton", command=self.encrypt_action).pack(side="right")

		right = ttk.LabelFrame(editor, text="Ciphertext")
		right.pack(side="right", fill="both", expand=True)

		self.cipher_text = tk.Text(right, wrap="word", height=12)
		self.cipher_text.pack(fill="both", expand=True, padx=10, pady=(10, 6))

		right_button_row = ttk.Frame(right)
		right_button_row.pack(fill="x", padx=10, pady=(0, 10))

		ttk.Button(right_button_row, text="Decrypt", style="ActionGreen.TButton", command=self.decrypt_action).pack(side="right")

		actions = ttk.Frame(container)
		actions.pack(fill="x", pady=(0, 8))

		ttk.Button(actions, text="Preview Digraphs", style="ActionYellow.TButton", command=self.preview_digraphs_action).pack(side="left")
		ttk.Button(actions, text="Clear", style="ActionGreen.TButton", command=self.clear_action).pack(side="left", padx=(8, 0))

		preview = ttk.LabelFrame(container, text="Prepared Digraphs")
		preview.pack(fill="both", expand=False, pady=(0, 10))

		self.digraph_text = tk.Text(preview, wrap="word", height=4, state="disabled")
		self.digraph_text.pack(fill="both", expand=True, padx=10, pady=10)

		ttk.Label(container, textvariable=self.status_var, style="Info.TLabel").pack(fill="x", pady=(4, 0))

	def _refresh_square(self) -> None:
		square, _positions = build_key_square(self.key_var.get().strip())

		for index, character in enumerate(character for row in square for character in row):
			self.matrix_labels[index].configure(text=character)

		self.status_var.set("Key square updated.")

	def _get_plaintext(self) -> str:
		return self.plain_text.get("1.0", "end").strip()

	def _set_plaintext(self, value: str) -> None:
		self.plain_text.delete("1.0", "end")
		self.plain_text.insert("1.0", value)

	def _get_ciphertext(self) -> str:
		return self.cipher_text.get("1.0", "end").strip()

	def _set_ciphertext(self, value: str) -> None:
		self.cipher_text.delete("1.0", "end")
		self.cipher_text.insert("1.0", value)

	def _write_digraph_preview(self, value: str) -> None:
		self.digraph_text.configure(state="normal")
		self.digraph_text.delete("1.0", "end")
		self.digraph_text.insert("1.0", value)
		self.digraph_text.configure(state="disabled")

	def _preview_encrypt_input(self, text: str) -> list[tuple[str, str]]:
		pairs = prepare_pairs(text)
		self._write_digraph_preview(format_pairs(pairs))
		return pairs

	def _preview_decrypt_input(self, text: str) -> list[tuple[str, str]]:
		pairs = chunk_text(text)
		self._write_digraph_preview(format_pairs(pairs))
		return pairs

	def _validate_key(self) -> str | None:
		key = self.key_var.get().strip()

		if not sanitize_text(key):
			messagebox.showwarning("Missing Key", "Please enter a key with at least one letter.")
			return None

		return key

	def _encrypt_from_plaintext(self) -> None:
		key = self._validate_key()
		if key is None:
			return

		text = self._get_plaintext()
		if not sanitize_text(text):
			messagebox.showwarning("Missing Plaintext", "Please enter plaintext to encrypt.")
			return

		square, positions = build_key_square(key)
		pairs = self._preview_encrypt_input(text)
		result = "".join("".join(encrypt_pair(first, second, positions, square)) for first, second in pairs)
		self._set_ciphertext(result)
		self.status_var.set("Plaintext encrypted into ciphertext.")

	def _decrypt_from_ciphertext(self) -> None:
		key = self._validate_key()
		if key is None:
			return

		text = self._get_ciphertext()
		if not sanitize_text(text):
			messagebox.showwarning("Missing Ciphertext", "Please enter ciphertext to decrypt.")
			return

		square, positions = build_key_square(key)
		cipher_pairs = self._preview_decrypt_input(text)
		raw_result = "".join("".join(decrypt_pair(first, second, positions, square)) for first, second in cipher_pairs)
		result = remove_inserted_fillers(raw_result)
		self._set_plaintext(result)
		self.status_var.set("Ciphertext decrypted into plaintext (fillers removed).")

	def preview_digraphs_action(self) -> None:
		plain = self._get_plaintext()
		cipher = self._get_ciphertext()

		if sanitize_text(plain):
			self._preview_encrypt_input(plain)
			self.status_var.set("Plaintext digraphs previewed.")
			return

		if sanitize_text(cipher):
			self._preview_decrypt_input(cipher)
			self.status_var.set("Ciphertext digraphs previewed.")
			return

		messagebox.showwarning("Missing Text", "Enter plaintext or ciphertext to preview digraphs.")

	def encrypt_action(self) -> None:
		self._encrypt_from_plaintext()

	def decrypt_action(self) -> None:
		self._decrypt_from_ciphertext()

	def clear_action(self) -> None:
		self.plain_text.delete("1.0", "end")
		self.cipher_text.delete("1.0", "end")
		self._write_digraph_preview("")
		self.status_var.set("Plaintext, ciphertext, and preview cleared.")


def main() -> None:
	app = PlayfairApp()
	app.mainloop()


if __name__ == "__main__":
	main()
