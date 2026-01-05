# """
# Part 4: Robust Error Handling
# =============================
# Difficulty: Intermediate+

# Learn:
# - Try/except blocks for API requests
# - Handling network errors
# - Timeout handling
# - Response validation
# """

# import requests
# from requests.exceptions import (
#     ConnectionError,
#     Timeout,
#     HTTPError,
#     RequestException
# )


# def safe_api_request(url, timeout=5):
#     """Make an API request with proper error handling."""
#     try:
#         response = requests.get(url, timeout=timeout)

#         # Raise exception for bad status codes (4xx, 5xx)
#         response.raise_for_status()

#         return {"success": True, "data": response.json()}

#     except ConnectionError:
#         return {"success": False, "error": "Connection failed. Check your internet."}

#     except Timeout:
#         return {"success": False, "error": f"Request timed out after {timeout} seconds."}

#     except HTTPError as e:
#         return {"success": False, "error": f"HTTP Error: {e.response.status_code}"}

#     except RequestException as e:
#         return {"success": False, "error": f"Request failed: {str(e)}"}


# def demo_error_handling():
#     """Demonstrate different error scenarios."""
#     print("=== Error Handling Demo ===\n")

#     # Test 1: Successful request
#     print("--- Test 1: Valid URL ---")
#     result = safe_api_request("https://jsonplaceholder.typicode.com/posts/1")
#     if result["success"]:
#         print(f"Success! Got post: {result['data']['title'][:30]}...")
#     else:
#         print(f"Failed: {result['error']}")

#     # Test 2: 404 Error
#     print("\n--- Test 2: Non-existent Resource (404) ---")
#     result = safe_api_request("https://jsonplaceholder.typicode.com/posts/99999")
#     if result["success"]:
#         print(f"Success! Data: {result['data']}")
#     else:
#         print(f"Failed: {result['error']}")

#     # Test 3: Invalid domain
#     print("\n--- Test 3: Invalid Domain ---")
#     result = safe_api_request("https://this-domain-does-not-exist-12345.com/api")
#     if result["success"]:
#         print(f"Success!")
#     else:
#         print(f"Failed: {result['error']}")

#     # Test 4: Timeout (using very short timeout)
#     print("\n--- Test 4: Timeout Simulation ---")
#     result = safe_api_request("https://httpstat.us/200?sleep=5000", timeout=1)
#     if result["success"]:
#         print(f"Success!")
#     else:
#         print(f"Failed: {result['error']}")


# def fetch_crypto_safely():
#     """Fetch crypto data with full error handling."""
#     print("\n=== Safe Crypto Price Checker ===\n")

#     coin = input("Enter coin (btc-bitcoin, eth-ethereum): ").strip().lower()

#     if not coin:
#         print("Error: Please enter a coin name.")
#         return

#     url = f"https://api.coinpaprika.com/v1/tickers/{coin}"
#     result = safe_api_request(url)

#     if result["success"]:
#         data = result["data"]
#         print(f"\n{data['name']} ({data['symbol']})")
#         print(f"Price: ${data['quotes']['USD']['price']:,.2f}")
#         print(f"24h Change: {data['quotes']['USD']['percent_change_24h']:+.2f}%")
#     else:
#         print(f"\nError: {result['error']}")
#         print("Tip: Try 'btc-bitcoin' or 'eth-ethereum'")


# def validate_json_response():
#     """Demonstrate JSON validation."""
#     print("\n=== JSON Validation Demo ===\n")

#     url = "https://jsonplaceholder.typicode.com/users/1"

#     try:
#         response = requests.get(url, timeout=5)
#         response.raise_for_status()
#         data = response.json()

#         # Validate expected fields exist
#         required_fields = ["name", "email", "phone"]
#         missing = [f for f in required_fields if f not in data]

#         if missing:
#             print(f"Warning: Missing fields: {missing}")
#         else:
#             print("All required fields present!")
#             print(f"Name: {data['name']}")
#             print(f"Email: {data['email']}")
#             print(f"Phone: {data['phone']}")

#     except requests.exceptions.JSONDecodeError:
#         print("Error: Response is not valid JSON")

#     except Exception as e:
#         print(f"Error: {e}")


# def main():
#     """Run all demos."""
#     demo_error_handling()
#     print("\n" + "=" * 40 + "\n")
#     validate_json_response()
#     print("\n" + "=" * 40 + "\n")
#     fetch_crypto_safely()


# if __name__ == "__main__":
#     main()


# --- EXERCISES ---
"""
Part 4 – Robust Error Handling (Exercises Solution)
==================================================
Exercise 1: Retry logic
Exercise 2: Crypto response validation
Exercise 3: Logging API requests
"""

import time
import requests
import logging


# -------------------- LOGGING SETUP (EXERCISE 3) --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -------------------- EXERCISE 1: SAFE API REQUEST WITH RETRY --------------------
def safe_api_request_with_retry(url, retries=3, timeout=5):
    """API request with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"Attempt {attempt}: Requesting {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json()}

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt} failed: {e}")

            if attempt < retries:
                time.sleep(2)  # wait before retry
            else:
                return {
                    "success": False,
                    "error": "All retry attempts failed."
                }


# -------------------- EXERCISE 2: VALIDATE CRYPTO RESPONSE --------------------
def validate_crypto_response(data):
    """Validate crypto API response structure."""
    if "quotes" not in data:
        return False, "Missing 'quotes' field"

    if "USD" not in data["quotes"]:
        return False, "Missing 'USD' field in quotes"

    if "price" not in data["quotes"]["USD"]:
        return False, "Missing price information"

    return True, "Valid response"


# -------------------- SAFE CRYPTO FETCH USING VALIDATION --------------------
def fetch_crypto_price():
    print("\n=== Crypto Price Checker ===")

    coin = input("Enter coin (btc-bitcoin / eth-ethereum): ").strip().lower()

    if not coin:
        print("Coin name cannot be empty")
        return

    url = f"https://api.coinpaprika.com/v1/tickers/{coin}"
    result = safe_api_request_with_retry(url)

    if not result["success"]:
        print("Error:", result["error"])
        return

    data = result["data"]
    valid, message = validate_crypto_response(data)

    if not valid:
        print("Error:", message)
        return

    price = data["quotes"]["USD"]["price"]
    print(f"{data['name']} ({data['symbol']})")
    print(f"Price: ${price:,.2f}")


# -------------------- EXERCISE 3: LOGGED API REQUEST --------------------
def safe_api_request_logged(url, timeout=5):
    """API request with logging."""
    try:
        logging.info(f"Sending request to {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        logging.info("Request successful")
        return {"success": True, "data": response.json()}

    except requests.exceptions.Timeout:
        logging.error("Request timed out")
        return {"success": False, "error": "Timeout"}

    except requests.exceptions.ConnectionError:
        logging.error("Connection error")
        return {"success": False, "error": "Connection failed"}

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e.response.status_code}")
        return {"success": False, "error": "HTTP error"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"success": False, "error": "Request failed"}


# -------------------- DEMO SECTION --------------------
def demo():
    print("\n=== Retry Logic Demo ===")
    result = safe_api_request_with_retry(
        "https://jsonplaceholder.typicode.com/posts/1"
    )

    if result["success"]:
        print("Success:", result["data"]["title"])
    else:
        print("Error:", result["error"])

    print("\n=== Logged Request Demo ===")
    logged_result = safe_api_request_logged(
        "https://jsonplaceholder.typicode.com/users/1"
    )

    if logged_result["success"]:
        print("User Name:", logged_result["data"]["name"])
    else:
        print("Error:", logged_result["error"])

    fetch_crypto_price()


# -------------------- MAIN --------------------
if __name__ == "__main__":
    demo()
