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

---

## 📋 Validation Rules

The validator supports three types of CSV files and applies specific validation rules to each:

### 🧑‍🤝‍🧑 **Contacts CSV Validation**

**Required Headers:** `userId`, `shouldJoin`, `joinDate`, `tierName`, `tierEntryAt`, `tierCalcAt`, `shouldReward`

**Validation Rules:**
- **userId**: Must not be empty, NULL, or duplicate
- **shouldJoin**: Must be exactly "TRUE"
- **joinDate**: Must be a valid past Unix timestamp **in milliseconds** (13 digits, not seconds)
- **tierName**: Can be any string value
- **tierEntryAt**: Must be empty
- **tierCalcAt**: Must be empty
- **shouldReward**: Must be either "TRUE" or "FALSE"

### 💰 **Points CSV Validation**

**Required Headers:** `userId`, `pointsToSpend`, `statusPoints`, `cashback`, `allocatedAt`, `expireAt`, `setPlanExpiration`, `reason`, `title`, `description`

**Validation Rules:**
- **userId**: Must not be empty
- **Points Values**: At least one of `pointsToSpend`, `statusPoints`, or `cashback` must have a positive value
- **Data Types**: `pointsToSpend` and `statusPoints` must be integers, `cashback` must be a float
- **No Negative Values**: All point values must be zero or positive
- **setPlanExpiration**: Must be "TRUE" or "FALSE"
  - If "TRUE": `expireAt` must be empty
  - If "FALSE": `expireAt` must be a valid future Unix timestamp **in milliseconds**
- **Timestamps**: All timestamp fields must use Unix milliseconds format (13 digits)

### 🎫 **Vouchers CSV Validation**

**Required Headers:** `userId`, `externalId`, `voucherType`, `voucherName`, `iconName`, `code`, `expiration`

**Validation Rules:**
- **User Identification**: Either `userId` or `externalId` must be provided (not both empty)
- **voucherType**: Must be either "one_time" or "yearly"
- **voucherName**: Must not be empty
- **iconName**: Must not be empty
- **code**: Must not be empty
- **expiration**: Must be a valid future Unix timestamp **in milliseconds**

### ⏰ **Timestamp Format Requirements**

**Critical:** All timestamps must be in **Unix milliseconds** format (13 digits), not seconds (10 digits).

**Examples:**
- ✅ Correct: `1735689600000` (milliseconds)
- ❌ Incorrect: `1735689600` (seconds - will be rejected)

**Common Error:** If you receive an error like *"Timestamp appears to be in seconds format"*, multiply your timestamp by 1000 to convert from seconds to milliseconds.

### 📁 **File Format Requirements**

- **Encoding**: UTF-8 or ISO-8859-1
- **Format**: Standard CSV with comma separators
- **BOM**: Byte Order Mark (BOM) will be automatically detected and cleaned
- **Headers**: Must exactly match the expected column names and order
- **Empty Rows**: Empty rows are automatically filtered out

### 🚫 **Common Validation Errors**

1. **Timestamp Format**: Using seconds instead of milliseconds
2. **Header Mismatch**: Incorrect column names or order
3. **Required Fields**: Missing required values in mandatory columns
4. **Data Types**: Using text where numbers are expected
5. **Date Logic**: Using future dates where past dates are required (or vice versa)
6. **Duplicate Data**: Multiple entries with the same userId (for contacts)

---

## 📖 Additional Resources

Further details on the loyalty migration process can be found at: https://help.sap.com/docs/SAP_EMARSYS/f8e2fafeea804018a954a8857d9dfff3/fdeaab3d74c110148adef25c35266ee0.html?q=loyalty+migration

---

## 🛠️ Development

### Setup

To set up the development environment with tests and git hooks:

```bash
./setup-dev.sh
```

This will:
- Create a virtual environment (`.venv`)
- Install pytest
- Configure git hooks to run tests on commit/push

### Running Tests

```bash
source .venv/bin/activate
pytest -v
```

### Git Hooks

Pre-commit and pre-push hooks are configured to run the test suite automatically. If tests fail, the commit/push will be blocked.

To manually enable hooks (if not using setup script):
```bash
git config core.hooksPath .githooks
```
