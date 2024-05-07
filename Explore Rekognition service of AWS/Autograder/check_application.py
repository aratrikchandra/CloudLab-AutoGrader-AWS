import requests
from bs4 import BeautifulSoup
import json

def read_app_config():
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
                    # Get the client's public IP
            try:
                client_ip = requests.get('https://api.ipify.org').text
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while getting client's public IP: {str(e)}")
                client_ip = None

            if "client_ip" not in data:
                data["client_ip"] = ""
            data['client_ip']=client_ip
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

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


def insert_image_id(new_image_id):
    try:
        with open('data.json', 'r+') as file:
            data = json.load(file)
            if "Uploaded Image Name" not in data:
                data["Uploaded Image Name"] = ""
            data["Uploaded Image Name"]=new_image_id
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

    except Exception as e:
        print(f"Failed to insert image ID to 'data.json': {e}")


def grade_tests(flash_messages, expected_conditions, test_case_number):
    score = 0
    print(f"Test Case {test_case_number}:")
    for condition in expected_conditions:
        if all(condition in message for message in flash_messages):
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
        files = {'file': ('valid_image.jpg', open(f'test_images/valid_image.jpg', 'rb'), 'image/jpeg')}
        response = requests.post(url, files=files)
        flash_messages, image_id = parse_flash_messages(response.content)
        total_score += grade_tests(flash_messages, ["Detected labels:"], 1)
        if image_id:
            insert_image_id(image_id)

    except Exception as e:
        print(f"An error occurred while testing: {e}")

if __name__ == "__main__":
    check_application()