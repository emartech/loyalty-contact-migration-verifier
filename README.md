# loyalty-contact-migration-verifier
Collection of CSV verifier scripts for https://help.sap.com/docs/SAP_EMARSYS/f8e2fafeea804018a954a8857d9dfff3/fdeaab3d74c110148adef25c35266ee0.html?q=Implementation-Migrating-contact-information-to-Loyalty+

---
Instructions:

1) Run the watcher.py script

```
python3 watcher.py
```

2) Put the CSV files in the watch_folder and wait while they are processed.

3) Once completed, the files will be moved to the "Success" or "Error" folder.
 
    Success = You can go ahead with the next steps on the migration

    Error = You will need to review the log files generated and share the feedback with the customer for them to amend/fix.
