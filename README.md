# Braille Translator

The Braille Translator project is a tool for detecting and translating Braille font on images. If you are interested in the Braille system or working with it, this project may be useful to you.

## Features

- **Detection of Braille font characters:** The program can detect Braille font characters and translate them.
- **Translation:** The project can translate the detected Braille font into two languages: Russian and English.
- **Open-source:** You can study and contribute to this project.

## Installation

1. Make sure you have Python installed (version 3.6 and above).
2. Clone the repository:
    ```
    git clone https://github.com/TiredOfThisAll/braille_translator.git
    ```
3. Download the model weights and the DLL for image binarization from the latest releases. Place them at the following path: `path_to_project/src/braille/bin_module/bin_module.dll` and `path_to_project/src/braille/weights/model.pth`.
4. Navigate to the project directory:
    ```
    cd braille_translator
    ```
5. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Run the program:
    ```
    python src/braille/main.py
    ```
2. Enter the path to the directory containing images with Braille font.
3. You can also use the web interface:
    ```
    python src/manage.py runserver
    ```

Now you are ready to use the Braille Translator!
