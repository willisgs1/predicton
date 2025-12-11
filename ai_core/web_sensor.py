import requests
from bs4 import BeautifulSoup
import random
import re
import numpy as np

class WebSensor:
    def __init__(self):
        # A list of seed URLs to start exploration.
        self.known_urls = [
            "https://en.wikipedia.org/wiki/Quantum_computing",
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://www.nature.com/subjects/quantum-information",
        ]
        self.visited_urls = set()

    def explore(self):
        """
        Visits a random known URL, extracts text, and finds new links.
        Returns the processed numerical data (the 'problem' to solve).
        """
        if not self.known_urls:
            self.known_urls = ["https://en.wikipedia.org/wiki/Quantum_computing"]

        url = random.choice(self.known_urls)
        print(f"[Sensor] Visiting: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                print(f"[Sensor] Failed to fetch {url} (Status: {response.status_code}). Using synthetic data.")
                return self.generate_synthetic_data(), "Synthetic Source (Network Error)"

            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. Harvest new links to keep the "life" going
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http') and href not in self.visited_urls:
                    self.known_urls.append(href)

            # Limit the known URLs to prevent memory explosion
            if len(self.known_urls) > 1000:
                self.known_urls = self.known_urls[-1000:]

            self.visited_urls.add(url)

            # 2. Extract content (Text)
            text_content = soup.get_text()

            # 3. Process content into a 'problem vector'
            problem_vector = self.process_content(text_content)

            return problem_vector, url

        except Exception as e:
            print(f"[Sensor] Error visiting {url}: {e}. Using synthetic data.")
            return self.generate_synthetic_data(), "Synthetic Source (Exception)"

    def process_content(self, text):
        """
        Converts text into a normalized numerical vector of size 8.
        """
        # Clean text
        text = re.sub(r'\s+', '', text).lower()
        if not text:
            return np.zeros(8)

        # Create a simple frequency vector for 8 common letters
        chars = "etaoinsh"
        vector = [text.count(c) for c in chars]

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        else:
            vector = np.array(vector, dtype=float)

        return np.array(vector)

    def generate_synthetic_data(self):
        """Generates random data if the internet is unreachable."""
        return np.random.rand(8)

if __name__ == "__main__":
    sensor = WebSensor()
    data, source = sensor.explore()
    print(f"Source: {source}")
    print(f"Data Vector: {data}")
