import os
import subprocess

def install_dependencies():
    print("Installing backend dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements/base.txt"])
    subprocess.run(["pip", "install", "-r", "requirements/dev.txt"])

    print("Installing frontend dependencies...")
    os.chdir("frontend")
    subprocess.run(["npm", "install"])
    os.chdir("..")

def configure_environment():
    print("Configuring environment variables...")
    with open("frontend/.env.development", "w") as env_file:
        env_file.write("VUE_APP_API_BASE_URL=http://localhost:8000/api\n")

def main():
    install_dependencies()
    configure_environment()
    print("Development environment setup complete.")

if __name__ == "__main__":
    main()
