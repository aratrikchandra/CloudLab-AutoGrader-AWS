import requests
import time
import json
from bs4 import BeautifulSoup

def upload_image(public_ip, port, image_path):
    url = f"http://{public_ip}:{port}/"
    files = {'file': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    return response

def check_labels(public_ip, port):
    url = f"http://{public_ip}:{port}/check_labels"
    response = requests.post(url)  # Use GET as per your Flask route
    return response

def parse_flash_message(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_message = soup.find(class_='flash')
    return flash_message.text if flash_message else None

def parse_html_labels(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    if not soup.find(text='No data available.'):
        try:
            image_name = soup.find('strong', text='Image:').next_sibling.strip()
            labels = soup.find('strong', text='Labels:').next_sibling.strip().split(", ")
            return image_name, labels
        except AttributeError:
            return None
    else:
        return None

def main():
    with open('data.json') as f:
        data = json.load(f)
    public_ip = data['public_ip']
    port = data['port']

    images = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    fetch_data = {}

    for image_path in images:
        response = upload_image(public_ip, port, image_path)
        response_text = response.text
        if 'File uploaded successfully. Please wait a few moments for processing.' not in response_text:
            print("Successful Upload message not seen i.e upload failed")
            continue

        time.sleep(2)  # Wait for label generation

        labels_response = check_labels(public_ip, port)
        if labels_response.url.endswith('/check_labels'):
            parsed_labels = parse_html_labels(labels_response.text)
            if parsed_labels:
                image_name, labels = parsed_labels
                fetch_data[image_name] = labels
            else:
                print("Error or no labels found for the image.")
                continue
        else:
            # Check for flash message
            flash_message = parse_flash_message(labels_response.text)
            if flash_message:
                print(flash_message)

    if fetch_data:
        with open('fetch.json', 'w') as f:
            json.dump(fetch_data, f, indent=4)

if __name__ == '__main__':
    main()
