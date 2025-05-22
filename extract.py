import subprocess
import argparse

help_text = subprocess.run(
  ["docker", "-h"], capture_output=True, text=True
).stdout



def main():
    print(help_text)

if __name__ == "__main__":
    main()

