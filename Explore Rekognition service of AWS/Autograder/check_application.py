import requests
from bs4 import BeautifulSoup
import json

def read_app_config():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            url = f"http://{data['public_ip']}:{data['port']}/"
            # Check if the URL is accessible
            response = requests.get(url)
            if response.status_code == 200:
                return url
            else:
                print(f"Error: Failed to connect to the application at {url}. Status code: {response.status_code}")
                exit()
    except FileNotFoundError:
        print("Error: 'data.json' file not found.")
        exit()
    except json.JSONDecodeError:
        print("Error: 'data.json' is not a valid JSON file.")
        exit()
    except Exception as e:
        print(f"Error occurred while checking connection: {e}")
        exit()

def parse_flash_messages(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_messages = []
    image_id = None
    for div in soup.find_all('div', class_='alert'):
        message = div.text.strip()
        flash_messages.append(message)
        if "File uploaded successfully." in message:
            id_start = message.find("Image ID: ") + len("Image ID: ")
            image_id = message[id_start:]
    return flash_messages, image_id

def append_image_id(new_image_id):
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
            if "uploaded_images" not in data:
                data["uploaded_images"] = []
            data["uploaded_images"].append(new_image_id)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
    except Exception as e:
        print(f"Failed to append image ID to 'data.json': {e}")

def grade_tests(flash_messages, expected_conditions, test_case_number):
    score = 0
    print(f"Test Case {test_case_number}:")
    for condition in expected_conditions:
        if any(condition in message for message in flash_messages):
            print("   Success:", flash_messages)
            score = 25
            break
    else:
        print("   Failure:", flash_messages)
    return score

def check_application():
    url = read_app_config()
    total_score = 0

    try:
        # Place your test images and files in the correct paths before running this script
        # Test 1: Valid image upload
        files = {'file': ('valid_image.jpg', open('test_images/valid_image.jpg', 'rb'), 'image/jpeg')}
        response = requests.post(url, files=files)
        flash_messages, image_id = parse_flash_messages(response.content)
        total_score += grade_tests(flash_messages, ["File uploaded successfully"], 1)
        if image_id:
            append_image_id(image_id)

        # Test 2: Large Image Upload
        files = {'file': ('large.jpg', open('test_images/large.jpg', 'rb'), 'image/jpeg')}
        response = requests.post(url, files=files)
        flash_messages, _ = parse_flash_messages(response.content)
        total_score += grade_tests(flash_messages, ["File size exceeds maximum allowed size"], 2)

        # Test 3: Invalid File Type
        files = {'file': ('invalid_image.pdf', open('test_images/invalid_image.pdf', 'rb'), 'application/pdf')}
        response = requests.post(url, files=files)
        flash_messages, _ = parse_flash_messages(response.content)
        total_score += grade_tests(flash_messages, ["Invalid file type"], 3)

        # Test 4: Empty File Submission
        response = requests.post(url, files={'file': ('', '', 'application/octet-stream')})
        flash_messages, _ = parse_flash_messages(response.content)
        total_score += grade_tests(flash_messages, ["No file part","No selected file"], 4)

        print("Total Score:", total_score, "/ 100")
    except Exception as e:
        print(f"An error occurred while testing: {e}")

if __name__ == "__main__":
    check_application()
