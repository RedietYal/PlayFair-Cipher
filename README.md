# Playfair Cipher GUI (Python)

A desktop GUI application to encrypt and decrypt text using the Playfair cipher.

## Features

- 5x5 Playfair key square (I/J combined)
- Plaintext -> Ciphertext encryption
- Ciphertext -> Plaintext decryption
- Digraph preview
- Filler handling for repeated letters (including repeated X case)
- Colored action buttons in the interface

## Project File

- Main app: playfair.py

## Requirements

- Python 3.10+ (works with your current environment)
- Tkinter (usually included with standard Python on Windows)

## Run Locally

From the project root:

```powershell
python playfair.py
```



## How It Works

- Sanitizes input to letters only, uppercase, with J merged into I.
- Builds digraphs for Playfair rules.
- Encrypts/decrypts using key-square row/column/rectangle logic.
- Decrypt flow removes likely filler characters inserted during encryption.

## Notes

- Classic Playfair has ambiguity when removing fillers. The app uses heuristic cleanup after decryption.
- If ciphertext length is odd, decryption pads internally to continue processing.

## License

Use freely for learning and educational purposes.
