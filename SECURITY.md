# Security Notice

An SSH private key was accidentally committed in earlier history.  
As of commit `4681fa1`, the key has been fully removed from the repository history using BFG.  
A new keypair has been issued and the old one revoked.  
All sensitive files are now included in `.gitignore` to prevent future leaks.

