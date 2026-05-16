import requests
import threading
import time
import sys

# Fix Windows console encoding for emojis
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
TARGET_URL = "http://13.53.39.78/api/stats"
CONCURRENT_USERS = 50
REQUESTS_PER_USER = 10

class LoadTester:
    def __init__(self):
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_time = 0
        self.lock = threading.Lock()

    def simulate_user(self, user_id):
        user_success = 0
        user_failed = 0
        
        for i in range(REQUESTS_PER_USER):
            try:
                start = time.time()
                response = requests.get(TARGET_URL, timeout=5)
                latency = time.time() - start
                
                if response.status_code == 200:
                    user_success += 1
                    with self.lock:
                        self.total_time += latency
                else:
                    user_failed += 1
            except Exception:
                user_failed += 1
                
            # Small sleep to simulate realistic user delay
            time.sleep(0.1)
            
        with self.lock:
            self.successful_requests += user_success
            self.failed_requests += user_failed

def main():
    print("========================================")
    print("      Cloud Load & Stress Tester")
    print("========================================\n")
    print(f"Targeting: {TARGET_URL}")
    print(f"Simulating {CONCURRENT_USERS} concurrent users...")
    print(f"Each user making {REQUESTS_PER_USER} requests.")
    print(f"Total expected requests: {CONCURRENT_USERS * REQUESTS_PER_USER}\n")
    print("Starting load test... (this may take a few seconds)\n")

    tester = LoadTester()
    threads = []
    
    start_time = time.time()

    # Create and start threads
    for i in range(CONCURRENT_USERS):
        thread = threading.Thread(target=tester.simulate_user, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_duration = end_time - start_time

    # Calculate metrics
    total_requests = tester.successful_requests + tester.failed_requests
    avg_latency = tester.total_time / tester.successful_requests if tester.successful_requests > 0 else 0
    req_per_sec = total_requests / total_duration if total_duration > 0 else 0
    success_rate = (tester.successful_requests / total_requests) * 100 if total_requests > 0 else 0

    print("========================================")
    print("             TEST RESULTS")
    print("========================================")
    print(f"Total Time Taken:  {total_duration:.2f} seconds")
    print(f"Total Requests:    {total_requests}")
    print(f"Successful:        {tester.successful_requests}")
    print(f"Failed:            {tester.failed_requests}")
    print(f"Success Rate:      {success_rate:.2f}%\n")
    
    print("PERFORMANCE METRICS:")
    print(f"Requests/Second:   {req_per_sec:.2f} req/s")
    print(f"Average Latency:   {avg_latency:.4f} seconds per request\n")
    
    if success_rate > 95:
        print("Conclusion: PASS ✅ - EC2 instance (t2.micro) successfully handled the load.")
    else:
        print("Conclusion: FAIL ❌ - EC2 instance struggled under load. Consider upgrading or adding a Load Balancer.")

if __name__ == "__main__":
    main()
