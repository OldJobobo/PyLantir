# PyLantir

PyLantir is an open-source client for the Atlantis Play-By-Email (PBEM) game, written in Python using PySide6. It reads JSON turn reports, displays game data, and features a 2D hex map to visualize discovered regions.

## Features

- **Parse and Display Turn Reports:** Easily import and view Atlantis PBEM game JSON turn reports.
- **Interactive 2D Hex Map:** Visualize the game world with a dynamic and interactive hexagonal map.
- **Unit and Settlement Markers:** Display unit positions and settlements on the map.
- **Detailed Hex Information:** View comprehensive data about each hex, including terrain, units, and market information.
- **Persistent Game Data:** Save and load game data to maintain map information across sessions.
- **User-Friendly GUI:** Navigate through the application with intuitive menus and dialogs.

## Project Structure

- `pylantir/ui/`: Contains the main window and user interface components.
- `pylantir/views/`: Implements the hex map visualization and related views.
- `pylantir/data/`: Manages game data and persistence.

## Installation

### Download the Latest Release (Windows)

For a straightforward Windows installation, you can download the most recent release of PyLantir:

1. **Visit the Latest Release Page:**
   
   Access the latest release of PyLantir on GitHub:
   
   [PyLantir Latest Release](https://github.com/OldJobobo/PyLantir/releases/latest)

2. **Download the Windows Installer:**
   
   - Locate the assets section in the latest release.
   - Download the appropriate installer for Windows (e.g., `PyLantir-Setup.exe`) or a ZIP archive.

3. **Install PyLantir:**
   
   - **If you downloaded an installer:**
     - Run the executable and follow the on-screen instructions.
   - **If you downloaded a ZIP archive:**
     - Extract its contents to a desired location.
     - Run the `PyLantir.exe` file from the extracted folder.


### Prerequisites

- Python 3.6 or higher
- Git (for cloning the repository)

### Clone the Repository

If you prefer to run PyLantir from source or contribute to its development, follow these steps to clone the repository and set it up locally.

1. **Prerequisites:**
   - **Python 3.6 or Higher:** Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
   - **Git:** Make sure Git is installed on your system. Download it from [git-scm.com](https://git-scm.com/downloads).

2. **Clone the Repository:**
   Open your terminal or command prompt and execute the following commands:
   ```bash
   git clone https://github.com/OldJobobo/PyLantir.git
   cd PyLantir
   ```

3. **Set Up a Virtual Environment (Optional but Recommended):**
   Creating a virtual environment helps manage dependencies without affecting your global Python installation.
   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install Dependencies:**
   Install the required Python packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run PyLantir:**
   Launch the application by running:
   ```bash
   python main.py
   ```
   Note: Ensure that main.py is the correct entry point. If the entry point differs, adjust the command accordingly.

## Usage

1. **Import Turn Reports:**
   - Navigate to the File menu.
   - Select Import Turn Report and choose your JSON turn report file.

2. **Explore the Map:**
   - Use the mouse or navigation controls to pan and zoom the 2D hex map.
   - Click on hex tiles to view detailed information about discovered regions.

3. **Access Menus and Settings:**
   - Utilize the menu bar to access additional features, settings, and help documentation.

## Contributing

Contributions are welcome! Please follow these steps to contribute to PyLantir:

1. **Fork the Repository:**
   Click the Fork button on the GitHub repository to create your own copy.

2. **Clone Your Fork:**
   ```bash
   git clone https://github.com/YourUsername/PyLantir.git
   cd PyLantir
   ```

3. **Create a New Branch:**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**
   Implement your feature or bug fix.

5. **Commit Your Changes:**
   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Submit a Pull Request:**
   Navigate to the original repository and create a pull request from your fork.