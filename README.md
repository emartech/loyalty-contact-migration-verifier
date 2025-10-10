# Loyalty-contact-migration-verifier
Collection of CSV verifier scripts for: https://help.sap.com/docs/SAP_EMARSYS/f8e2fafeea804018a954a8857d9dfff3/fdeaab3d74c110148adef25c35266ee0.html?q=Implementation-Migrating-contact-information-to-Loyalty+

---
🧩 Prerequisites:

You must have Python installed on your computer to run this application.

🔗 Download Python

Windows: https://www.python.org/downloads/windows/

MacOS: https://www.python.org/downloads/macos/

To check if Python is already installed, open your Terminal (macOS) or Command Prompt (Windows) and run:
```
python3 --version
```
If Python is installed, you’ll see the version number displayed.

---

⚙️ Instructions:

1) [Download](https://github.com/emartech/loyalty-contact-migration-verifier/archive/refs/heads/main.zip) the files from this repository and save them to a folder on your computer (e.g., your Desktop).
 <img width="1833" height="588" alt="image" src="https://github.com/user-attachments/assets/891718c5-e248-4e84-8ce8-0e756ca64979" />
  


2) Open your Terminal and navigate to the folder where you saved the downloaded files.
   
3) Run the watcher.py script:

```
python3 watcher.py
```

4) Add your CSV files to the watch_folder and wait while they are processed.

5) Once processing is complete, the files will be automatically moved to either the “Success” or “Error” folder, depending on the outcome.
 
   ✅ Success: The files have the correct structure required to proceed with the migration. Please contact SAP Emarsys Support and provide the verified files.

   ❌ Error: Please review the generated log files and make the necessary amendments, updates, or fixes before proceeding.
   


⚠️ When you encounter any error or issue related to the migration script for contacts or points, please ensure you are using the [latest version of the verifier/validator](https://github.com/emartech/loyalty-contact-migration-verifier/archive/refs/heads/main.zip) available in this repository.
