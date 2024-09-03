#!/usr/bin/env python3
import argparse, requests, re, os
from urllib.parse import urlparse, parse_qs, urlencode
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

def get_args():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Find reflected parameters in a URL.")
    parser.add_argument('-u', '--url', required=True, help="The URL to scan.")
    parser.add_argument('-w', '--wordlist', default=os.path.expanduser("./statics/params.txt"),
                        help="Path to the wordlist file (default: ./statics/params.txt).")
    return parser.parse_args()

def load_wordlist(wordlist_path):
    # Load the wordlist from the specified file path
    if not os.path.isfile(wordlist_path):
        print(f"Wordlist file not found: {wordlist_path}")
        exit(1)
    
    with open(wordlist_path, 'r') as f:
        wordlist = [line.strip() for line in f if line.strip()]
    
    return wordlist

def fetch_url(url):
    # Send a GET request to the given URL
    try:
        response = requests.get(url)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def extract_page_parameters(html_content):
    # Parse the HTML content to find name and id attributes, and JavaScript variable names
    soup = BeautifulSoup(html_content, 'html.parser')
    parameters = set()

    # Extract all 'name' and 'id' attributes from tags
    for tag in soup.find_all(True, {'name': True}):
        parameters.add(tag['name'])
    for tag in soup.find_all(True, {'id': True}):
        parameters.add(tag['id'])

    # Extract JavaScript variable names (rudimentary regex-based method)
    js_vars = re.findall(r'\bvar\s+(\w+)\s*=', html_content)
    parameters.update(js_vars)

    return parameters

def find_reflections(url, wordlist, page_params):
    # Check for reflections of parameters in the response content
    reflected_params = []
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    
    # Combine wordlist parameters and page-derived parameters
    params_to_check = {param: wordlist for param in page_params}
    
    with ThreadPoolExecutor() as executor:
        # Check each parameter using multiple threads
        futures = {executor.submit(check_reflection, base_url, key, value): key for key, value in params_to_check.items()}
        for future in futures:
            param, is_reflected = future.result()
            if is_reflected:
                reflected_params.append(param)
    
    return reflected_params

def check_reflection(base_url, param, wordlist):
    # Send a request with each parameter from the wordlist and check for reflection in the response
    for word in wordlist:
        test_params = {param: word}
        test_url = f"{base_url}?{urlencode(test_params)}"
        response = fetch_url(test_url)
        if response and word in response:
            return param, True
    return param, False

def main():
    # Main function to execute the script
    args = get_args()
    url = args.url
    wordlist_path = args.wordlist
    
    # Load wordlist from the file specified in the command-line argument or default path
    wordlist = load_wordlist(wordlist_path)
    
    # Fetch the original page content to find parameters from the HTML
    html_content = fetch_url(url)
    if html_content is None:
        exit("Failed to fetch the URL content.")
    
    # Extract parameters from the page (name, id, JS variable names)
    page_params = extract_page_parameters(html_content)
    
    # Add wordlist to the parameters for reflection checking
    page_params.update(parse_qs(urlparse(url).query).keys())

    # Find and list all reflected parameters
    reflected_params = find_reflections(url, wordlist, page_params)
    
    if reflected_params:
        print("Reflected Parameters Found:")
        for param in reflected_params:
            print(f"- {param}")
    else:
        print("No reflected parameters found.")

if __name__ == "__main__":
    main()
