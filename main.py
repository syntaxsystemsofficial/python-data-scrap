from flask import Flask
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# CORS(app, origins=["http://127.0.0.1:5000"])


def get_all_vehicle_data(vrm):
    # Initialize the SeleniumBase Driver with UC mode (undetected Chrome)
    driver = Driver(uc=True, headless=True)

    try:
        # Open the website
        url = "https://www.caranalytics.co.uk"
        # Reconnect if blocked by Cloudflare
        driver.uc_open_with_reconnect(url, 10)

        # Wait for the page to load and handle CAPTCHA (if any)
        driver.uc_gui_click_captcha()  # Solve CAPTCHA if present

        # Locate the input field and enter the registration number
        input_field = driver.find_element(By.CSS_SELECTOR, "#vrm-input")
        input_field.send_keys(vrm)  # Enter the registration number

        # Locate and click the submit button
        submit_button = driver.find_element(
            By.CSS_SELECTOR, "#searchForm > div > button")
        submit_button.click()

        # Wait for the results to load
        time.sleep(10)  # Adjust the sleep time as needed

        # Locate all report card elements
        report_cards = driver.find_elements(By.CLASS_NAME, "report_card")

        image = driver.find_element(
            By.CSS_SELECTOR, "#page-content > div > div > div.wizard_pointer_details > div.car_number_wrapper.text-center > div.d-flex.justify-content-center.mt-4.mb-3 > img")
        image_url = image.get_attribute('src')  # Fixed typo here
        print(f"Image URL: {image_url}")

        # Dictionary to store all data
        all_data = {}

        # Loop through each report card and extract data
        for report_card in report_cards:
            # Extract the heading
            try:
                heading = report_card.find_element(
                    By.CLASS_NAME, "vehicle_heading.grey-vehicle-heading").text.strip()
                print(f"Heading: {heading}")
            except:
                print(f"Heading Not Found")
                continue

            # Initialize a dictionary to store data for this heading
            heading_data = {}

            # Extract data based on the heading
            if "Tax & MOT" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            # Extract the key (e.g., "MOT Status")
                            key = columns[0].text.strip()
                            # Extract the value (e.g., "Expires 27 Apr 2025")
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Tax & MOT Table Not Found")

            elif "Mileage Checks" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Mileage Checks Table Not Found")

            elif "Vehicle Specification" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Vehicle Specification Table Not Found")

            elif "Vehicle Registration" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Vehicle Registration Table Not Found")

            elif "Economic and environmental details" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.oppose.mt-3")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            # Extract the key (e.g., "Extra Urban")
                            key = columns[0].text.strip()
                            # Extract the value (e.g., "-")
                            value = columns[1].text.strip()
                            if key and value:  # Skip empty rows
                                # Store the data in the dictionary
                                heading_data[key] = value
                except:
                    print("Economic and Environmental Table Not Found")

            elif "Mileage History" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.autow.oppose")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    mileage_data = []
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        # Ensure there are exactly 3 columns (Date, Mileage recorded, Yearly Total)
                        if len(columns) == 3:
                            date = columns[0].text.strip()
                            mileage = columns[1].text.strip()
                            yearly_total = columns[2].text.strip()
                            mileage_data.append((date, mileage, yearly_total))
                    heading_data["Mileage History"] = mileage_data
                except:
                    print("Mileage History Table Not Found")

            elif "MOT History of the Vehicle" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.autow.mot_history_tabl.oppose")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    mot_data = []
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 5:  # Ensure there are exactly 5 columns
                            date = columns[0].text.strip()
                            test_result = columns[1].text.strip()
                            mileage = columns[2].text.strip()
                            advisory_notices = columns[3].text.strip()
                            failure_notices = columns[4].text.strip()
                            mot_data.append(
                                (date, test_result, mileage, advisory_notices, failure_notices))
                    heading_data["MOT History"] = mot_data
                except:
                    print("MOT History Table Not Found")

            # Add the heading data to the main dictionary
            all_data[heading] = heading_data
            all_data[heading] = {
                'heading_data': heading_data,
                'image_url': image_url
            }

        return all_data

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Close the browser
        driver.quit()


def get_vehicle_data(vrm):
    # Initialize the SeleniumBase Driver with UC mode (undetected Chrome)
    driver = Driver(uc=True, headless=True)

    try:
        # Open the website
        url = "https://www.caranalytics.co.uk"
        # Reconnect if blocked by Cloudflare
        driver.uc_open_with_reconnect(url, 10)

        # Wait for the page to load and handle CAPTCHA (if any)
        driver.uc_gui_click_captcha()  # Solve CAPTCHA if present

        # Locate the input field and enter the registration number
        input_field = driver.find_element(By.CSS_SELECTOR, "#vrm-input")
        input_field.send_keys(vrm)  # Enter the registration number

        # Locate and click the submit button
        submit_button = driver.find_element(
            By.CSS_SELECTOR, "#searchForm > div > button")
        submit_button.click()

        # Wait for the results to load
        time.sleep(10)  # Adjust the sleep time as needed

        # Locate all report card elements
        report_cards = driver.find_elements(By.CLASS_NAME, "report_card")

        image = driver.find_element(
            By.CSS_SELECTOR, "#page-content > div > div > div.wizard_pointer_details > div.car_number_wrapper.text-center > div.d-flex.justify-content-center.mt-4.mb-3 > img")
        image_url = image.get_attribute('src')  # Fixed typo here
        print(f"Image URL: {image_url}")

        # Dictionary to store all data
        all_data = {}

        # Loop through each report card and extract data
        for report_card in report_cards:
            # Extract the heading
            try:
                heading = report_card.find_element(
                    By.CLASS_NAME, "vehicle_heading.grey-vehicle-heading").text.strip()
                print(f"Heading: {heading}")
            except:
                print(f"Heading Not Found")
                continue

            # Initialize a dictionary to store data for this heading
            heading_data = {}

            # Extract data based on the heading
            if "Tax & MOT" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            # Extract the key (e.g., "MOT Status")
                            key = columns[0].text.strip()
                            # Extract the value (e.g., "Expires 27 Apr 2025")
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Tax & MOT Table Not Found")

            elif "Mileage Checks" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Mileage Checks Table Not Found")

            elif "Vehicle Specification" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Vehicle Specification Table Not Found")

            elif "Vehicle Registration" in heading:
                try:
                    table = report_card.find_element(
                        By.CSS_SELECTOR, ".table.table-stripedd.table-values-bold")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) == 2:  # Ensure there are exactly 2 columns (key and value)
                            key = columns[0].text.strip()  # Extract the key
                            # Extract the value
                            value = columns[1].text.strip()
                            # Store the data in the dictionary
                            heading_data[key] = value
                except:
                    print("Vehicle Registration Table Not Found")

            all_data[heading] = heading_data
            all_data[heading] = {
                'heading_data': heading_data,
                'image_url': image_url
            }

        return all_data

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Close the browser
        driver.quit()


@app.route("/get-all-vehicle-data", methods=["POST"])
def handle_all_vehicle_data_request():
    data = request.json  # Get the JSON data from the frontend
    vrm = data.get("vrm")  # Extract the registration number

    if not vrm:
        return jsonify({"error": "Registration number is required"}), 400

    # Fetch the vehicle data
    vehicle_data = get_all_vehicle_data(vrm)
    return jsonify(vehicle_data)


@app.route("/get-vehicle-data", methods=["POST"])
def handle_vehicle_data_request():
    data = request.json  # Get the JSON data from the frontend
    vrm = data.get("vrm")  # Extract the registration number

    if not vrm:
        return jsonify({"error": "Registration number is required"}), 400

    # Fetch the vehicle data
    vehicle_data = get_vehicle_data(vrm)
    return jsonify(vehicle_data)


@app.route('/')
def home():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)


