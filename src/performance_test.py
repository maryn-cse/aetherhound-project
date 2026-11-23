import time
import subprocess
import sys

start_time = time.perf_counter()

result = subprocess.run(
    [sys.executable, "src/frequency_detector.py"],
    capture_output=True,
    text=True
)

end_time = time.perf_counter()

print(result.stdout)

if result.returncode == 0:
    print("--------------------------------------")
    print(f"Detection Time: {end_time - start_time:.4f} seconds")
    print("Performance test completed!")
else:
    print("Error while running detector:")
    print(result.stderr)