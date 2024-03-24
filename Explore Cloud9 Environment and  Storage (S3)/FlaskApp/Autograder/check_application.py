import requests
from bs4 import BeautifulSoup

# Function to parse flash messages from HTML content
def parse_flash_messages(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_messages = []
    for div in soup.find_all('div', class_='alert'):
        flash_messages.append(div.text.strip())
    return flash_messages

# Function to check if the application is publicly accessible and working properly
def check_application(url):
    try:
        # Test 1: Image file size less than 2MB
        files = {'file': open('test_images/valid_image.jpg', 'rb')}
        response = requests.post(url, files=files)
        flash_messages = parse_flash_messages(response.content)
        print("Test 1 (Image size < 2MB):", response.status_code)
        print("   Flash messages:", flash_messages)

        # Test 2: Image file size greater than 2MB
        files = {'file': open('test_images/large.jpg', 'rb')}
        response = requests.post(url, files=files)
        flash_messages = parse_flash_messages(response.content)
        print("Test 2 (Image size > 2MB):", response.status_code)
        print("   Flash messages:", flash_messages)

        # Test 3: Not an image file
        files = {'file': open('test_images/invalid_image.pdf', 'rb')}
        response = requests.post(url, files=files)
        flash_messages = parse_flash_messages(response.content)
        print("Test 3 (Not an image file):", response.status_code)
        print("   Flash messages:", flash_messages)

        # Test 4: Empty file submission
        response = requests.post(url)
        flash_messages = parse_flash_messages(response.content)
        print("Test 4 (Empty file submission):", response.status_code)
        print("   Flash messages:", flash_messages)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    # Replace 'http://<public_ip>:<port>/' with your Flask application URL
    check_application('http://54.227.184.72:8080/')
