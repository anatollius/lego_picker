import csv
import time
from dataclasses import dataclass

from PySide6.QtWidgets import QApplication, QFileDialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

PIECE_ID_COLUMN = "id"
QUANTITY_COLUMN = "quantity"


@dataclass
class Piece:
    id: str
    quantity: int


# Load CSV data
def load_csv() -> list[Piece]:
    _app = QApplication([])
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Select CSV file", "", "CSV files (*.csv)"
    )
    if not file_path:
        return

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        return [Piece(row[PIECE_ID_COLUMN], row[QUANTITY_COLUMN]) for row in reader]


# Set up the browser (Chrome in this case)
def setup_browser():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    browser = webdriver.Chrome(service=service, options=options)
    return browser


# Add a LEGO piece to the basket
def add_pieces_to_basket(browser, pieces: list[Piece]):
    wait = WebDriverWait(browser, 10)

    age_gate_button = wait.until(
        EC.presence_of_element_located((By.ID, "age-gate-grown-up-cta"))
    )
    age_gate_button.click()

    cookies_button = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-test='cookie-necessary-button']")
        )
    )
    cookies_button.click()

    # Find the search input, enter the part ID, and submit
    search_box = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-test='pab-search-input-field']")
        )
    )

    time.sleep(1)

    for piece in pieces:
        search_box.clear()
        time.sleep(1)
        search_box.send_keys(piece.id)
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        try:
            # Select the piece based on search result
            part_link = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='pab-item-btn-pick']")
                )
            )
            time.sleep(1)
            part_link.click()
            time.sleep(1)

            # Adjust quantity
            qty_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-test='pab-item-quantity']")
                )
            )
            time.sleep(1)
            qty_input.clear()
            time.sleep(1)
            qty_input.send_keys(str(piece.quantity))

            # Add to basket
            add_to_basket_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='mini-cart-add-to-main-cart']")
                )
            )
            time.sleep(1)
            add_to_basket_btn.click()

            time.sleep(1)

            continue_shopping_btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "[data-test='pab-add-to-bag-modal-button-continue']",
                    )
                )
            )
            time.sleep(1)
            continue_shopping_btn.click()
            time.sleep(1)

        except Exception as e:
            print(f"Error adding part {piece.id}: {e}")

    print("\nAll pieces added to cart\n")


# Main function to execute the script
def main():
    # Load CSV data
    pieces_data = load_csv()

    # Set up the browser and open the LEGO Pick-a-Brick page
    browser = setup_browser()
    browser.get("https://www.lego.com/en-gb/pick-and-build/pick-a-brick")

    add_pieces_to_basket(browser, pieces_data)

    # Close the browser after completion
    print("All parts added to basket.")
    pass


# Run the main function
if __name__ == "__main__":
    main()
